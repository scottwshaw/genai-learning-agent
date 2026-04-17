output "server_ip" {
  description = "Public IPv4 address of the research agent server"
  value       = hcloud_server.research_agent.ipv4_address
}

output "server_id" {
  description = "Hetzner server ID"
  value       = hcloud_server.research_agent.id
}
