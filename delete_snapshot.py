import json
import boto3
from io import BytesIO
import gzip
import yaml
import argparse

def fetch_snap_id(bucket,key):
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket,key)
        n = obj.get()['Body'].read()
        gzipfile = BytesIO(n)
        gzipfile = gzip.GzipFile(fileobj=gzipfile)
        content = gzipfile.read()
        content=yaml.safe_load(content)
        snaps=[]
        for snapid in content:
            snaps.append(snapid.get('status').get("snapshotHandle"))
    except Exception as e:
        print(e)
        raise e
    return snaps

def delete_snaps(snaps,region):
     try:
        ec = boto3.client('ec2',region)
        for snap in snaps:
            ec.delete_snapshot(SnapshotId= snap)
            print("Snapshot {} deleted".format(snap))
     except Exception as e:
         print(e)
         raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bucket', dest='bucket', help='bucket')
    parser.add_argument('-bn', '--backup_name', dest='backup_name', help='backup_name')
    parser.add_argument('-r', '--region', dest='region', help='region')
    args = parser.parse_args()
    bucket=args.bucket
    backup_name=args.backup_name
    region=args.region
    key="backups/"+backup_name+"/"+backup_name+"-csi-volumesnapshotcontents.json.gz"
    snaps=fetch_snap_id(bucket,key)
    delete_snaps(snaps,region)
