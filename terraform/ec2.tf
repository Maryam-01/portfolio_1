resource "aws_instance" "example" {
  ami = "resolve:ssm:/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
  instance_type = "t3.micro"

  key_name = "MA-7"
  associate_public_ip_address = true
  vpc_security_group_ids = [
  aws_security_group.ec2_app.id
]

user_data = <<-EOF
#!/bin/bash
set -e
exec > /home/ubuntu/progress.txt 2>&1

REPO_URL="https://github.com/Maryam-01/portfolio_1.git"
APP_DIR="/home/ubuntu/app"

DB_HOST="${aws_db_instance.db-test1.address}"
DB_PORT="${aws_db_instance.db-test1.port}"
DB_NAME="postgres"
DB_USER="postgres"
DB_PASSWORD="${var.db_password}"
JWT_SECRET="super_secret_jwt_key"

DATABASE_URL="postgresql://$${DB_USER}:$${DB_PASSWORD}@$${DB_HOST}:$${DB_PORT}/$${DB_NAME}"

apt update -y
apt install -y python3 python3-pip python3-venv git

rm -rf $${APP_DIR}
git clone $${REPO_URL} $${APP_DIR}
cd $${APP_DIR}

python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

echo "Seeding database..."

env \
  DATABASE_URL="$${DATABASE_URL}" \
  DB_HOST="$${DB_HOST}" \
  DB_PORT="$${DB_PORT}" \
  DB_NAME="$${DB_NAME}" \
  DB_USER="$${DB_USER}" \
  DB_PASSWORD="$${DB_PASSWORD}" \
  JWT_SECRET="$${JWT_SECRET}" \
  venv/bin/python seed.py

echo "Starting FastAPI..."

nohup env \
  DATABASE_URL="$${DATABASE_URL}" \
  DB_HOST="$${DB_HOST}" \
  DB_PORT="$${DB_PORT}" \
  DB_NAME="$${DB_NAME}" \
  DB_USER="$${DB_USER}" \
  DB_PASSWORD="$${DB_PASSWORD}" \
  JWT_SECRET="$${JWT_SECRET}" \
  venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 \
  > /home/ubuntu/app.log 2>&1 &
EOF


  tags = {
    Name = "nc-project-ec2-ssh"
    Environment = "dev"
    Owner= "maryam"
    Project= "portfolio-1"
  }
}

output "ec2_ip" {
  value = aws_instance.example.public_ip
}



data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "postgres-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "Postgres subnet group"
  }
}



resource "aws_security_group" "allow_postgres_traffic" {
  name        = "allow-postgres-traffic"
  description = "allow postgreSQL traffic only"

ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_app.id]
  }
egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
}
}

resource "aws_db_instance" "db-test1" {
    identifier = "postgres-test2"
    allocated_storage = 20
    db_subnet_group_name = aws_db_subnet_group.default.name
    engine = "postgres"
    engine_version = "14"
    instance_class = "db.t3.micro"
    username = "postgres"
    password = var.db_password
    vpc_security_group_ids = [aws_security_group.allow_postgres_traffic.id]
    publicly_accessible = false
    skip_final_snapshot = true
}

output "rds_endpoint" {
    value = aws_db_instance.db-test1.endpoint

}

output "rds_port" {
    value = aws_db_instance.db-test1.port
}

# -------------------
# SECURITY GROUPS
# -------------------

resource "aws_security_group" "ec2_app" {
  name        = "ec2_app_sg"
  description = "Security group for EC2 app"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["82.6.15.214/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}