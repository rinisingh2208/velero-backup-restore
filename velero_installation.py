import os
import tarfile
import shutil
import argparse
import sys
import time
import logging
import subprocess


def exeCommand(command):
    logging.debug("\nCommand = " + str(command))
    output, error = subprocess.Popen(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE, shell=True).communicate()
    logging.debug("\nOutput = " + str(output))
    logging.debug("\nError = " + str(error))
    return output, error


def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        from pip._internal import main
        main(['install', package])
    # finally:
    #    globals()[package] = importlib.import_module(package)


def download_and_extract():
    path = "velero1.6.3"
    os.mkdir(path)
    # url = "https://github.com/vmware-tanzu/velero/releases/download/v1.4.2/velero-v1.4.2-linux-amd64.tar.gz"
    # wget.download(url, path)
    cmd = "wget https://github.com/vmware-tanzu/velero/releases/download/v1.6.3/velero-v1.6.3-linux-amd64.tar.gz -P "+path
    exeCommand(cmd)

    my_tar = tarfile.open('velero1.6.3/velero-v1.6.3-linux-amd64.tar.gz')
    my_tar.extractall(path)  # specify which folder to extract to
    my_tar.close()


def download_and_extract_for_aws():
    path = "velero"
    os.mkdir(path)

    # url = "https://github.com/vmware-tanzu/velero/releases/download/v1.4.2/velero-v1.4.2-linux-amd64.tar.gz"
    # wget.download(url, path)

    cmd = "wget https://github.com/vmware-tanzu/velero/releases/download/v1.6.3/velero-v1.6.3-linux-amd64.tar.gz -P velero"
    exeCommand(cmd)
    my_tar = tarfile.open('velero/velero-v1.6.3-linux-amd64.tar.gz')
    my_tar.extractall(path)  # specify which folder to extract to
    my_tar.close()


def create_credentials():
    path = "velero1.6.3/velero-v1.6.3-linux-amd64"
    os.chdir(path)

    shutil.copy("velero", "/usr/bin/")
    f = open("credentials-velero", "w+")
    f.write("[default]\n")
    f.write("aws_access_key_id = minio\n")
    f.write("aws_secret_access_key = minio123\n")
    f.close()
    os.chdir('../..')


def minio_start():
    cmd1 = "kubectl apply -f scripts/00-minio-deployment.yaml"
    # os.system(cmd1)
    result = exeCommand(cmd1)
    logging.debug("\n Minio installation : " + str(result))


if __name__ == '__main__':

    install_and_import('wget')

    parser = argparse.ArgumentParser()

    # -p provider  -b bucket  -r region  -url url  -purl public url -a access key  -s secret access key
    parser.add_argument("-m", "--mode", dest="mode", help="mode where you want the data to be stored")
    parser.add_argument("-b", "--bucket", dest="bucket",
                        help="provide the name of the bucket to which you want to store data in")
    parser.add_argument("-r", "--region", dest="region", help=" provide the region in which your bucket is located")
    parser.add_argument("-url", "--url", dest="url", default=0, required=False, help="metion the url")
    parser.add_argument("-cluster_name", "--cluster_name", dest="cluster_name", required=True,
                        help="mention the cluster name on which going to install velero client")
    # parser.add_argument("-a", "--access_key", dest="accesskey", default=0, help="access key for aws")
    # parser.add_argument("-s", "--secret_access_key", dest="secretaccesskey", default=0,
    #                    help="secret access key for aws")
    parser.add_argument("-purl", "--publicurl", dest="publicurl", default=0, help="ip of the vm and the port")
    args = parser.parse_args()

    # p=args.provider
    m = args.mode
    b = args.bucket
    r = args.region
    url = args.url
    # a = args.accesskey
    # s = args.secretaccesskey
    purl = args.publicurl
    cluster_name = args.cluster_name
    cmd = "aws configure get aws_access_key_id"
    a = exeCommand(cmd)
    a = a[0].replace("\n", "")
    cmd1 = "aws configure get aws_secret_access_key"
    s = exeCommand(cmd1)
    s = s[0].replace("\n", "")
    # print(s)
    cmd3 = "rm -rf velero"
    rem = exeCommand(cmd3)
    cmd4 = "aws eks --region "+r+" update-kubeconfig --name " + cluster_name
    kubeconfig = exeCommand(cmd4)
    if m == 'aws':
        logging.basicConfig(filename="/var/log/velero.log", format='%(asctime)s %(message)s', level=logging.DEBUG)

        download_and_extract_for_aws()

        if a == 0:
            print("access_key argument is must please enter")
            sys.exit(1)
        elif s == 0:
            print("secret_access_key argument is must please enter")
            sys.exit(1)
        elif (a == 0 and s == 0):
            print("access_key and secret_access_key are must please enter")
            sys.exit(1)
        path = "velero/velero-v1.6.3-linux-amd64"
        os.chdir(path)

        f = open("credentials-velero", "w+")
        f.write("[default]\n")
        f.write("aws_access_key_id = " + a + "\n")
        f.write("aws_secret_access_key = " + s + "\n")
        f.close()
        shutil.copy("velero", "/usr/local/bin/")
        os.chdir('../..')

        cmd = "velero install \
         --provider aws \
         --plugins quay.io/anuta/aws-velero:latest,velero/velero-plugin-for-csi:v0.1.2 \
         --bucket " + b + " \
         --secret-file velero/velero-v1.6.3-linux-amd64/credentials-velero \
         --backup-location-config region=" + r + " \
         --snapshot-location-config region=" + r + " \
         --use-restic \
         --features=EnableCSI \
         --wait"
        os.system(cmd)
        sys.exit(1)
    elif m == 'awsall':
        download_and_extract_for_aws()

        if a == 0:
            print("access_key argument is must please enter")
            sys.exit(1)
        elif s == 0:
            print("secret_access_key argument is must please enter")
            sys.exit(1)
        elif (a == 0 and s == 0):
            print("access_key and secret_access_key are must please enter")
            sys.exit(1)
        path = "velero/velero-v1.6.3-linux-amd64"
        os.chdir(path)
        shutil.copy("velero", "/usr/local/bin/")
        f = open("credentials-velero", "w+")
        f.write("[default]\n")
        f.write("aws_access_key_id = " + a + "\n")
        f.write("aws_secret_access_key = " + s + "\n")
        f.close()
        os.chdir('../..')

        cmd = "velero install \
             --provider aws \
             --plugins quay.io/anuta/aws-velero:latest,velero/velero-plugin-for-csi:v0.1.2 \
             --bucket " + b + " \
             --secret-file velero/velero-v1.6.3-linux-amd64/credentials-velero \
             --use-volume-snapshots=true \
             --backup-location-config region=" + r + " \
             --snapshot-location-config region=" + r + " \
             --features=EnableCSI \
             --wait"
        print
        cmd
        os.system(cmd)
        sys.exit(1)
    else:
        if url == 0 and purl == 0:
            print
            "url and purl is must please enter "
            sys.exit(1)
        elif url == 0:
            print
            "url is must please enter"
            sys.exit(1)
        elif purl == 0:
            print
            "purl is mush please enter"
            sys.exit(1)

        download_and_extract()

        create_credentials()

        minio_start()
        time.sleep(20)

        cmd = "velero install \
         --provider aws \
         --plugins quay.io/anuta/aws-velero:latest,velero/velero-plugin-for-csi:v0.1.2 \
         --bucket " + b + " \
         --secret-file velero1.6.3/velero-v1.6.3-linux-amd64/credentials-velero \
         --use-volume-snapshots=false \
         --backup-location-config region=" + r + ",s3ForcePathStyle=\'true\',s3Url=" + url + ",publicUrl=" + purl + " \
         --use-restic \
         --features=EnableCSI \
         --wait "
        os.system(cmd)
        sys.exit(1)
