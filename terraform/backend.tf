terraform {
  backend "s3" {
    bucket  = "nc-portfolio-tfstate-maryam"
    key     = "global/terraform.tfstate"
    region  = "eu-west-2"
    encrypt = true
  }
}