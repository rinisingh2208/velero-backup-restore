#!/bin/bash

usage() { echo "Usage: $0 [-b <bucket>] [-l <region>] [-u <username>] [-p <policyname>]" 1>&2 ; exit 1;}
while getopts ":b:l:u:p:" o;
do
    case "${o}" in
        b)
            b=${OPTARG}

            ;;
        l)
            l=${OPTARG}

            ;;
        u)
            u=${OPTARG}

            ;;
        p)
            p=${OPTARG}

            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))
if [ -z "${u}" ]; then
            u="appbackup"
            #usage
fi

if [ -z "${p}" ] ; then
     p="appbackup"
fi




BUCKET=${b}
REGION=${l}

a=`aws s3api list-buckets --query Buckets[].Name --output text --region=${l}`

if [[ "$a" =~ .*"$b".* ]]; then
  echo "Bucket $b already there."
else
    aws s3api create-bucket --bucket ${b} --region ${l} --create-bucket-configuration LocationConstraint=${l}

fi


user=`aws iam list-users --query Users[].UserName --output text`
if [[ "$user" =~ .*"$u".* ]]; then
  echo "User $u already there."
else
      aws iam create-user --user-name ${u}


fi

cat > velero-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVolumes",
                "ec2:DescribeSnapshots",
                "ec2:CreateTags",
                "ec2:CreateVolume",
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObject",
                "s3:AbortMultipartUpload",
                "s3:ListMultipartUploadParts"
            ],
            "Resource": [
                "arn:aws:s3:::${b}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::${b}"
            ]
        }
    ]
}
EOF


kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml

cat > volume-snapshot-class.yaml <<EOF
apiVersion: snapshot.storage.k8s.io/v1beta1
kind: VolumeSnapshotClass
metadata:
  name: minio-snapclass
  labels:
          velero.io/csi-volumesnapshot-class: "true"
driver: ebs.csi.aws.com
deletionPolicy: Delete
EOF

kubectl create -f volume-snapshot-class.yaml

aws iam put-user-policy --user-name ${u} --policy-name ${p} --policy-document file://velero-policy.json
aws iam create-access-key --user-name ${u}


