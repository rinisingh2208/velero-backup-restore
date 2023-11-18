import time
import os
import subprocess
import logging
import re
import argparse
import sys

from datetime import datetime


def exeCommand(command):
    logging.debug("\nCommand = " + str(command))
    output, error = subprocess.Popen(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE, shell=True).communicate()
    logging.debug("\nOutput = " + str(output))
    logging.debug("\nError = " + str(error))
    return output, error







def present_date_And_time():
    present_date_And_time.date_and_time = datetime.now().strftime('%d-%m-%Y--%H-%M-%S')
  










def executeCommand(command):
    logging.debug("\nCommand = " + str(command))
    wait = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = wait.communicate()
    logging.debug("\nOutput = " + str(output))
    logging.debug("\nError = " + str(error))
    return output, error



def backupPolling(backupName):
    backupStatusCommand = "velero backup describe " + backupName + " | grep -i Phase | cut -f2 -d: | cut -f3 -d' '"
    logging.info("Velero backup polling...")
    print
    "Velero backup polling..."
    timeout = time.time() + 60 * 120  # assuming 120 min timeout for worst case scenario
    result = ""
    while ("Completed" not in result):
        statusOutput, statusError = executeCommand(backupStatusCommand)
        result = statusOutput.replace("\n", "").strip()
        print
        result
        if "error" in result or "not found" in result or "Failed" in result:
            break
        time.sleep(10)
        if time.time() > timeout:
            logging.error("timeout for backup 120mins. Time exceeded")
            break





def fetch_cluster_owner(cluster_name,region):
    cmd = "aws eks describe-cluster --name " + cluster_name + "  --query cluster.tags.Owner --region "+region
    #print(cmd)
    statusOutput, statusError = executeCommand(cmd)
    print("owner " + statusOutput)
    print("error owner "+statusError)
    return statusOutput


def fetch_cluster_creation_datetime(cluster_name,region):
    cmd = "aws eks describe-cluster --name " + cluster_name + "  --query cluster.createdAt --region "+region
    #print(cmd)
    wait = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = wait.communicate()
    print("\nOutput creation datetime = " + str(output))
    print("\nError creation datetime= " + str(error))
    return output




def setting_kube_config(cluster_name,region):
    cmd="sudo aws eks --region  "+region+" update-kubeconfig --name "+cluster_name
    statusOutput, statusError = executeCommand(cmd)
    print("Config done " + statusOutput)
    print("Config error " + statusError)
    return statusOutput


def complete_backup(cluster_name, build_user,region):
    present_date_And_time()

    if n == 'all':
        #labels setting
        setting_kube_config(cluster_name,region)
        owner = fetch_cluster_owner(cluster_name,region)
        cluster_creation_datetime = fetch_cluster_creation_datetime(cluster_name,region)
      
        time = present_date_And_time.date_and_time
        cluster_name_label = "cluster_name=" + cluster_name
        cluster_name_label = cluster_name_label.replace("\n", "").replace('"', "")
        cluster_owner_name = "cluster_owner_name=" + owner
        cluster_owner_name = cluster_owner_name.replace("\n", "").replace('"', "")
        cluster_creation_datetime = "cluster_creation_datetime=" + cluster_creation_datetime
        cluster_creation_datetime = cluster_creation_datetime.replace("\n", "").replace('"', "")
        cluster_creation_datetime = cluster_creation_datetime.replace(":", "_")  # labels not taking : in time
        backup_creation_owner = "backup_creation_owner=" + build_user
        backup_creation_owner = backup_creation_owner.replace("\n", "").replace('"', "")
        #backup_creation_time = "backup_creation_time=" + time
        #backup_creation_time = backup_creation_time.replace("\n", "").replace('"', "")
        #backup_creation_time = backup_creation_time.replace(":", "_")
       
        # labels=labels.replace("\n","").replace('"',"")
        # print("labels "+labels)
        time = time.replace("--", "-")
        cmd = "velero backup create " + cluster_name + "-" + time + " --labels " + cluster_name_label + "," + cluster_owner_name + "," + cluster_creation_datetime + "," + backup_creation_owner 
        print("backup command " + cmd)
        os.system(cmd)
        name = cluster_name + "-" + time
        backupPolling(name)


def backuplist():
    cmd = "velero backup get | awk '{print $1}' | tail -n +2"
    backuplist.result = exeCommand(cmd)
    backuplist.getnames = list(backuplist.result)
    backuplist.get_names = backuplist.getnames[0].split("\n")
    del backuplist.get_names[-1]


def restorePolling(restoreName):
    result = ""
    restoreStatusCommand = "velero restore describe " + restoreName + " | grep -i Phase | cut -f2 -d: | cut -f3 -d' '"
    logging.info("Velero restore polling...")
    print
    "Velero restore polling..."
    timeout = time.time() + 60 * 120  # assuming 120min timeout for worst case scenario
    while ("Completed" not in result):
        statusOutput, statusError = executeCommand(restoreStatusCommand)
        result = statusOutput.replace("\n", "").strip()
        print(result)
        if "error" in result or "not found" in result or "Failed" in result:
            break
        time.sleep(10)
        if time.time() > timeout:
            logging.error("timeout for restore 120mins. Time exceeded")
            break


def restore_names_list():
    getting_names_for_backup()
    present_date_And_time()
    restore_names_list.names_for_restore = []
    for i in getting_names_for_backup.pods:
        regex = '[-]{*}[0-9]{1,}[-][0-9]{1,}'
        res = re.findall(regex, i)
        if i == res or i == '' or i == ' ':
            continue
        restore_names_list.result = i + "-" + present_date_And_time.date_and_time + '-restore'
        restore_names_list.names_for_restore.append(restore_names_list.result)







def complete_restore(n,cluster_name):
    present_date_And_time()
    cmd = "kubectl delete pv --all"
    exeCommand(cmd)

    if n == 'all':
        name = 'apprestore' + present_date_And_time.date_and_time
        cmd = "velero restore create " + name + " --from-backup " + rn
        print
        cmd
        os.system(cmd)
       

        # exeCommand(cmd1)
       
def cleanupallsnapshort():
    cleanupcommand = "velero backup delete --all --confirm"
    print
    cleanupcommand
    executeCommand(cleanupcommand)


def cleanupsnapshort(backupname):
    cleanupsnapshortcommand = "velero backup delete " + backupname + " --confirm"
    print
    cleanupsnapshortcommand
    executeCommand(cleanupsnapshortcommand)


def cleanupallrestoresnapshort():
    cleanuprestorecommand = "velero restore delete --all --confirm"
    print
    cleanuprestorecommand
    executeCommand(cleanuprestorecommand)


def cleanuprestoresnaphsort(restorebackupname):
    cleanuprestoresnapshortcommand = "velero restore delete " + restorebackupname + " --confirm"
    print
    cleanuprestoresnapshortcommand
    executeCommand(cleanuprestoresnapshortcommand)


def delete_velero_installation():
    deletepolicy = "aws iam delete-user-policy --user-name " + username + " --policy-name " + policyname
    print
    deletepolicy
    executeCommand(deletepolicy)

    namespaceclusterbind = "kubectl delete namespace/velero clusterrolebinding/velero"
    print
    namespaceclusterbind
    executeCommand(namespaceclusterbind)

    crdscomponent = "kubectl delete crds -l component=velero"
    print
    crdscomponent
    executeCommand(crdscomponent)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # -m mode (backup or restore) -n name
    parser.add_argument("-m", "--mode", dest="mode", help="weather to take backup or restore")
    parser.add_argument("-n", "--name", dest="name", default='all', required=False, help="of the the backup or restore")
    parser.add_argument("-rn", "--restorebackupname", dest="restorebackupname", required=False,
                        help="of the the backup or restore")
    # parser.add_argument("-b", "--backupOption", dest="backupOption", default='local', required=True, help="enter weather cluster is in local or aws")
    parser.add_argument("-dt", "--dateandtime", dest="dateandtime", default='', required=False, help=" date and time")
    parser.add_argument("-un", "--username", dest="username", default='', help="username which you want to delete")
    parser.add_argument("-pn", "--policyname", dest="policyname", default='', help="policy name you want to delete")
    parser.add_argument("-c", "--cluster_name", dest="cluster_name", default='',
                        help="cluster name for which creating backup")
    parser.add_argument("-b", "--build_user", dest="build_user", default='',
                        help="build user for backup jon")
    parser.add_argument("-r", "--region", dest="region", default='',
                        help="region of cluster to fetch labels")
    args = parser.parse_args()
    m = args.mode
    n = args.name
    username = args.username
    policyname = args.policyname
    rn = args.restorebackupname
    cluster_name = args.cluster_name
    build_user = args.build_user
    region=args.region
    # backupOption = args.backupOption
    dt = args.dateandtime

    if m == 'backup':
        if n == 'all':
            complete_backup(cluster_name, build_user,region)
        else:
            print("go ahead add logic for your application pods backup")
    elif m == 'restore':
        if n == 'all':
            complete_restore(n,cluster_name)
        else:
            print(" go ahead add logic for your application pods restore")
    elif m == 'deletebackup':
        if n == 'all':
            cleanupallsnapshort()
        else:
            cleanupsnapshort(n)
    elif m == 'deleterestore':
        if n == 'all':
            cleanupallrestoresnapshort()
        else:
            cleanuprestoresnaphsort(n)
    elif m == 'deletevelero' and (username != '' and policyname != ''):
        delete_velero_installation()
    else:
        print("arguments not pass for mode so exiting...")
