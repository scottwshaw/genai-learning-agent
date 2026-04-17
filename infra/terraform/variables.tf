variable "ssh_public_key" {
  description = "SSH public key for server access (fetched from 1Password)"
  type        = string
}

variable "server_name" {
  description = "Name of the Hetzner server"
  type        = string
  default     = "research-agent"
}

variable "server_type" {
  description = "Hetzner server type"
  type        = string
  default     = "cx23"

}

variable "location" {
  description = "Hetzner data centre location"
  type        = string
  default     = "nbg1"
}
