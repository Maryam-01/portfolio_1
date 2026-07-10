resource "aws_instance" "example" {
  ami = "resolve:ssm:/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
  instance_type = "t3.micro"

  key_name = "MA-7"
  vpc_security_group_ids = [
    aws_security_group.ssh_only.id,
    aws_security_group.allow_http.id
    ]

user_data = <<-EOF
#!/bin/bash
exec > /home/ubuntu/progress.txt 2>&1

REPO_URL="https://github.com/lewispricey/HelloFromTheS3Side.git"
APP_DIR="/home/ubuntu/app"

apt update -y
apt upgrade -y
apt install -y python3 python3-pip python3-venv git

git clone $REPO_URL $APP_DIR
cd $APP_DIR

python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

nohup venv/bin/uvicorn src.app:app --host 0.0.0.0 --port 8000 &
EOF

user_data_replace_on_change = true


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

resource "aws_security_group" "ssh_only" {
    name = "allow_ssh"
    description = "allow ssh"




ingress {
    
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["87.117.231.69/32"]
}

egress {

    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
}


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

resource "aws_security_group" "allow_http" {
    name = "allow_http"
    description = "allow FASTAPI traffic"

ingress {
    
    from_port = 8000
    to_port = 8000
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
}

egress {

    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
}
}

resource "aws_security_group" "allow_postgres_traffic" {
    name = "allow-allow_postgres_traffic"
    description = "allow postgreSQL traffic only"

ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    security_groups = [aws_security_group.ssh_only.id]
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