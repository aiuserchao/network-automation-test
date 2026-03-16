# Network Automation - Terraform Configuration
# Provider: Juniper Apstra

terraform {
  required_providers {
    apstra = {
      source  = "Juniper/apstra"
      version = "~> 0.30.0"
    }
  }
}

# Example: Create a blueprint
resource "apstra_datacenter_blueprint" "example" {
  name        = "example-blueprint"
  template_id = "L2_Virtual_EVPN"
}

# Example: Create a routing zone
resource "apstra_datacenter_routing_zone" "example" {
  blueprint_id = apstra_datacenter_blueprint.example.id
  name         = "example-rz"
  vlan_id      = 100
}

output "blueprint_id" {
  value = apstra_datacenter_blueprint.example.id
}