#!/bin/bash

usage() { echo "Usage: $0 [-b <bucket>] [-l <region>] [-c <custer_name>]" 1>&2 ; exit 1;}
while getopts ":b:l:c:" o;
do
    case "${o}" in
        b)
            b=${OPTARG}

            ;;
        l)
            l=${OPTARG}

            ;;
        c)
            c=${OPTARG}

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


# Setting environment variables

# Name of the cluster
CLUSTERNAME=${c}
# Namespace where Velero will be deployed in
NAMESPACE=velero
# Name of the service account
SERVICEACCOUNT=velero
# Name of the bucket where the backups will be stored
BUCKET=${b}
# Region of the bucket
REGION=${l}
# AWS CLI Profile
PROFILE="default"
# Sets the AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text --profile $PROFILE)

aws iam create-policy \
  --policy-name VeleroBackupPolicy \
  --policy-document file://velero-policy.json \
  --profile $PROFILE

  # Set the OIDC Provider
OIDC_PROVIDER=$(aws eks describe-cluster --name $CLUSTERNAME --query "cluster.identity.oidc.issuer" --profile $PROFILE --output text | sed -e "s/^https:\/\///")

cat > trust.json <<EOF
{
  "Version": "2021-10-11",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${OIDC_PROVIDER}:sub": "system:serviceaccount:velero:veleros3"
        }
      }
    }
  ]
}
EOF

# Create the role and attach the trust relationship
aws iam create-role --role-name ServiceAccount-Velero-Backup \
  --assume-role-policy-document file://trust.json \
  --description "Service Account to give Velero the necessary permissions to operate." \
  --profile $PROFILE

# Attach the Velero policy to the role.
aws iam attach-role-policy \
  --role-name ServiceAccount-Velero-Backup \
  --policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/VeleroBackupPolicy \
  --profile $PROFILE

# Create the OIDC provider for the cluster
# Once created, this is listed under IAM > Identity Providers
eksctl utils associate-iam-oidc-provider \
  --cluster $CLUSTERNAME \
  --approve \
  --profile $PROFILE


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
