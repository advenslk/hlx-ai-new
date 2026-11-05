"""
HELZERX AI Support - Knowledge Base Repository
Contains verified HELZERX technical documentation, hosting specs, troubleshooting, and policies.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from bot.knowledge.rag_engine import RAGEngine, DocumentChunk

# Seed verified HELZERX documentation
VERIFIED_DOCUMENTS: List[Dict[str, str]] = [
    {
        "title": "HELZERX Minecraft Paper & Purpur Server Performance Guide",
        "category": "minecraft",
        "tags": "paper,purpur,minecraft,jvm,aikar,performance,lag",
        "content": """
### HELZERX Minecraft Paper & Purpur Optimization
For Minecraft Paper/Purpur instances on HELZERX Game Cloud:
1. Java Version Requirements:
   - Minecraft 1.12.2 - 1.16.4: Java 8 or Java 11.
   - Minecraft 1.17 - 1.20.4: Java 17 (Zulu or Temurin).
   - Minecraft 1.20.5 - 1.21+: Java 21 (Temurin 21 HotSpot).
2. Recommended Aikar's JVM Flags:
   ```bash
   -Xms{RAM}G -Xmx{RAM}G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true
   ```
3. Out of Memory (OOM) Errors:
   If Pterodactyl console shows `Killed` or `Out of memory: Killed process`, ensure server startup allocation (-Xmx) leaves at least 1024MB for off-heap container overhead and JVM thread memory.
4. Profiling:
   Install Spark profiler (`/spark profiler --timeout 60`) or Spark health (`/spark health`) to identify lag causes, entity tile lag, or rogue chunk generation.
"""
    },
    {
        "title": "HELZERX Pterodactyl Wings Troubleshooting & Configuration",
        "category": "technical",
        "tags": "pterodactyl,wings,docker,systemd,ssl,ehostunreach",
        "content": """
### HELZERX Pterodactyl Wings Troubleshooting
Common Pterodactyl Wings issues and step-by-step resolution:
1. Wings Service Status:
   Check service status: `sudo systemctl status wings`
   Inspect real-time logs: `sudo journalctl -u wings -n 100 --no-pager`
2. EHOSTUNREACH / Connection Refused:
   - Verify Wings is listening on port 8080 (or 443 if SSL proxy is configured):
     `sudo ss -tulpn | grep wings`
   - Check firewall rules: `sudo ufw allow 8080/tcp` and verify node IP matches Panel node FQDN.
3. SSL Certificate Expiry / Certbot:
   If Wings logs report `x509: certificate has expired or is not yet valid`:
   - Run `sudo certbot renew`
   - Restart wings: `sudo systemctl restart wings`
   - Ensure the private key path in `/etc/pterodactyl/config.yml` points to `/etc/letsencrypt/live/<fqdn>/privkey.pem`.
4. Docker Daemon Unresponsive:
   Ensure Docker socket is active: `sudo systemctl restart docker && sudo systemctl restart wings`.
"""
    },
    {
        "title": "HELZERX Cloudflare DNS & Minecraft Domain Linking",
        "category": "technical",
        "tags": "cloudflare,dns,srv,domain,proxy,orange cloud",
        "content": """
### Cloudflare DNS Configuration for HELZERX Game Servers
When connecting custom domains (e.g., play.mycommunity.com) to HELZERX servers:
1. Proxy Status (Orange Cloud vs Grey Cloud):
   - CRITICAL: Cloudflare's HTTP/HTTPS Proxy (Orange Cloud) ONLY forwards web traffic (ports 80, 443, etc.).
   - Raw game protocols (Minecraft TCP 25565, Rust UDP, ARK, FiveM) CANNOT pass through Cloudflare Orange Cloud without expensive Cloudflare Spectrum.
   - You MUST set the DNS record to "DNS Only" (Grey Cloud).
2. Dedicated Port (Default 25565):
   If you have a dedicated IP / port 25565:
   - Type: A record
   - Name: `play` (or `@`)
   - IPv4 address: `YOUR_HELZERX_SERVER_IP`
   - Proxy status: DNS only (Grey Cloud)
3. Non-Standard Port (SRV Record):
   If your server has a shared IP with custom port (e.g., 25577):
   - First, create an A record: `mc.yourdomain.com` -> `SERVER_IP` (Grey Cloud).
   - Second, create an SRV record:
     * Service: `_minecraft`
     * Protocol: `TCP`
     * Name: `play`
     * Priority: `0`
     * Weight: `5`
     * Port: `25577` (your allocated port)
     * Target: `mc.yourdomain.com`
"""
    },
    {
        "title": "HELZERX Linux VPS Provisioning & Security Baseline",
        "category": "vps",
        "tags": "vps,linux,ubuntu,debian,ssh,ufw,swap,security",
        "content": """
### HELZERX Linux VPS Initial Setup & Hardening
1. Initial SSH Access:
   Connect via terminal: `ssh root@YOUR_VPS_IP`
2. Update System Packages:
   `sudo apt update && sudo apt upgrade -y`
3. Configure UFW Firewall:
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```
4. Configure Swap Space (For 2GB-4GB VPS):
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```
5. SSH Key Authentication:
   Disable password login in `/etc/ssh/sshd_config` by setting `PasswordAuthentication no` after placing public keys in `~/.ssh/authorized_keys`.
"""
    },
    {
        "title": "HELZERX Dedicated Servers Hardware & Anti-DDoS Architecture",
        "category": "dedicated",
        "tags": "dedicated,hardware,ddos,sla,ipmi,idrac,bare metal",
        "content": """
### HELZERX Dedicated Server Specifications & Mitigation
1. Hardware Architecture:
   - AMD EPYC 7003/9004 Series & Intel Xeon Scalable Processors.
   - Enterprise NVMe PCIe 4.0 in RAID 1 / RAID 10 configuration.
   - Dual 10Gbps redundant uplinks with BGP Anycast routing.
2. Anti-DDoS Mitigation:
   - Multi-layer 3.2 Tbps mitigation capacity powered by inline Corero & Voxility scrubbing filters.
   - Automatic mitigation triggers in under 1 second without dropping TCP sessions.
   - Custom game filters: Source Engine query filter, RakNet, Minecraft SYN/ACK flood protection.
3. IPMI / KVM Access:
   - Dedicated out-of-band management console available via customer portal under Server Details > IPMI Console.
"""
    },
    {
        "title": "HELZERX Billing, Refund Policy & Service SLA",
        "category": "billing",
        "tags": "billing,refund,invoice,sla,terms,cancellation",
        "content": """
### HELZERX Billing & Refund Policy
1. 7-Day Money-Back Guarantee:
   - Standard VPS and Game Hosting instances are eligible for a 100% full refund within 7 calendar days of first order if the service does not meet expectations.
   - Dedicated Bare Metal Servers, domain registrations, and custom IP blocks are non-refundable due to physical provisioning costs.
2. Invoicing & Due Dates:
   - Invoices generate 7 days before service expiration.
   - Grace period: Servers remain online for 48 hours past due date before automatic suspension. Data is retained for 7 days before termination.
3. Payment Methods:
   - Credit / Debit Cards (Stripe), PayPal, and Cryptocurrency (BTC, ETH, USDT).
"""
    }
]


class KnowledgeManager:
    """Manages the HELZERX technical documentation store and RAG retrieval."""

    def __init__(self):
        self.rag = RAGEngine()
        self.documents = list(VERIFIED_DOCUMENTS)
        self._init_index()

    def _init_index(self):
        for doc in self.documents:
            self.rag.index_document(doc["title"], doc["category"], doc["content"])

    def add_document(self, title: str, category: str, content: str, tags: str = "") -> None:
        doc = {
            "title": title,
            "category": category,
            "tags": tags,
            "content": content
        }
        self.documents.append(doc)
        self.rag.index_document(title, category, content)

    def search(self, query: str, category: Optional[str] = None, top_k: int = 2) -> str:
        """Searches for relevant context and formats it as markdown."""
        results = self.rag.search(query, top_k=top_k)
        if not results:
            return ""

        formatted_parts = []
        for chunk, score in results:
            formatted_parts.append(f"### [DOCUMENT: {chunk.title}]\n{chunk.content}")

        return "\n\n".join(formatted_parts)


knowledge_manager = KnowledgeManager()
