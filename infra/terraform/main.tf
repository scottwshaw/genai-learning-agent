terraform {
  required_version = ">= 1.0"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

# HCLOUD_TOKEN is read from the environment — never stored in config.
# Export it before running terraform:
#   export HCLOUD_TOKEN=$(op item get 'HETZNER_API_KEY' --vault Private --fields credential --reveal)
#   export TF_VAR_ssh_public_key=$(op item get 'Hetzner From Personal Laptop' --vault Private --fields 'public key' --reveal)
provider "hcloud" {}

resource "hcloud_ssh_key" "deploy" {
  name       = "${var.server_name}-deploy"
  public_key = var.ssh_public_key
}

resource "hcloud_firewall" "research_agent" {
  name = "${var.server_name}-fw"

  # SSH from anywhere (secured by key-only auth + fail2ban)
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  # All outbound allowed (API calls, git push, 1Password)
  rule {
    direction       = "out"
    protocol        = "tcp"
    port            = "any"
    destination_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction       = "out"
    protocol        = "udp"
    port            = "any"
    destination_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction       = "out"
    protocol        = "icmp"
    destination_ips = ["0.0.0.0/0", "::/0"]
  }
}

resource "hcloud_server" "research_agent" {
  name        = var.server_name
  server_type = var.server_type
  location    = var.location
  image       = "ubuntu-24.04"

  ssh_keys = [hcloud_ssh_key.deploy.id]

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    SSH_PUBLIC_KEY = var.ssh_public_key
  })

  firewall_ids = [hcloud_firewall.research_agent.id]

  labels = {
    purpose = "research-agent"
  }
}
