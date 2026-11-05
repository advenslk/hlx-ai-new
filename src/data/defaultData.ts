export interface TicketCategory {
  id: string;
  name: string;
  description: string;
  emoji: string;
  defaultPriority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  department: string;
}

export const TICKET_CATEGORIES: TicketCategory[] = [
  {
    id: 'general',
    name: 'General Support',
    description: 'Account inquiries, service info, and general assistance',
    emoji: '👥',
    defaultPriority: 'NORMAL',
    department: 'Customer Service'
  },
  {
    id: 'cloud_hosting',
    name: 'Cloud & Hosting',
    description: 'VPS, Dedicated servers, Minecraft & cloud infrastructure',
    emoji: '📚',
    defaultPriority: 'HIGH',
    department: 'Infrastructure Operations'
  },
  {
    id: 'technical',
    name: 'Technical Issues',
    description: 'OS, networking, Docker, SSL, and general server problems',
    emoji: '🖥️',
    defaultPriority: 'NORMAL',
    department: 'Technical Support'
  },
  {
    id: 'billing',
    name: 'Billing & Payments',
    description: 'Invoices, payment gateways, subscriptions, renewals, refunds',
    emoji: '💳',
    defaultPriority: 'NORMAL',
    department: 'Billing & Finance'
  },
  {
    id: 'partnership',
    name: 'Partnerships & Business',
    description: 'Affiliate programs, sponsorships, enterprise inquiries',
    emoji: '🚀',
    defaultPriority: 'LOW',
    department: 'Management'
  },
  {
    id: 'minecraft',
    name: 'Minecraft Hosting',
    description: 'Paper/Purpur, Pterodactyl, plugin issues, crash reports, ports',
    emoji: '⛏️',
    defaultPriority: 'NORMAL',
    department: 'Game Server Operations'
  },
  {
    id: 'vps',
    name: 'VPS Support',
    description: 'KVM VPS provisioning, reinstallation, kernel, network routing',
    emoji: '🖥️',
    defaultPriority: 'HIGH',
    department: 'Infrastructure Team'
  }
];

export interface MessageItem {
  id: string;
  authorName: string;
  authorRole: 'customer' | 'ai' | 'staff' | 'system';
  content: string;
  timestamp: string;
  detectedLang?: 'en' | 'si' | 'singlish';
  latencyMs?: number;
  isInternalNote?: boolean;
}

export interface TicketItem {
  id: string;
  code: string;
  category: string;
  categoryName: string;
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  status: 'OPEN' | 'CLAIMED' | 'ESCALATED' | 'CLOSED';
  creator: string;
  subject: string;
  description: string;
  serverIdentifier?: string;
  claimedBy?: string;
  aiEnabled: boolean;
  createdAt: string;
  closedAt?: string;
  messages: MessageItem[];
  internalNotes: { id: string; author: string; content: string; timestamp: string }[];
}

export const INITIAL_TICKETS: TicketItem[] = [
  {
    id: 't-1',
    code: 'HZX-8429',
    category: 'minecraft',
    categoryName: 'Minecraft Hosting',
    priority: 'HIGH',
    status: 'OPEN',
    creator: 'AlexV',
    subject: 'Paper 1.20.4 server crashes upon player join (OutOfMemoryError)',
    description: 'Server boots fine, but as soon as 3 players join, container gets killed with exit code 137.',
    serverIdentifier: 'node-colombo-02 / srv-4192',
    aiEnabled: true,
    createdAt: '10 mins ago',
    messages: [
      {
        id: 'm-1',
        authorName: 'AlexV',
        authorRole: 'customer',
        content: '**Subject:** Paper 1.20.4 server crashes upon player join (OutOfMemoryError)\n\nServer boots fine, but as soon as 3 players join, container gets killed with exit code 137.',
        timestamp: '10 mins ago',
        detectedLang: 'en'
      },
      {
        id: 'm-2',
        authorName: 'HELZERX AI Support',
        authorRole: 'ai',
        content: `Hello Alex! Exit code **137** indicates the Linux kernel Out-Of-Memory (OOM) killer terminated the container because memory exceeded the allocated cgroup limit.\n\nHere is how to resolve this step-by-step:\n\n1. **Check Off-Heap JVM Overhead**:\nIf your server allocation is **4GB**, your \`-Xmx\` startup flag must NOT be set to \`-Xmx4096M\`. Java requires off-heap memory for garbage collection, Netty threads, and metaspace. Set \`-Xmx\` to **3072M** (\`-Xmx3G\`) to leave 1GB head-room.\n\n2. **Apply Verified Aikar Flags** in your Pterodactyl Startup tab:\n\`\`\`bash\n-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40\n\`\`\`\n\n3. **Inspect Crash Reports**: Check \`/crash-reports/latest.txt\` or run \`/spark health\` once restarted to check loaded chunks.\n\nLet me know if you would like me to escalate this to an on-duty engineer!`,
        timestamp: '9 mins ago',
        detectedLang: 'en',
        latencyMs: 142
      }
    ],
    internalNotes: [
      {
        id: 'in-1',
        author: 'Staff_Devon',
        content: 'Customer is on node-colombo-02. Node memory usage is currently 64%, no host-level pressure.',
        timestamp: '8 mins ago'
      }
    ]
  },
  {
    id: 't-2',
    code: 'HZX-3105',
    category: 'vps',
    categoryName: 'VPS Support',
    priority: 'URGENT',
    status: 'ESCALATED',
    creator: 'NuwanK',
    subject: 'Mage VPS eke UFW firewall eka on karala SSH block una',
    description: 'sudo ufw enable kalaata passe ssh port eken disconnect una. Dan connect wenna ba bro.',
    serverIdentifier: 'vps-49201 (185.220.101.44)',
    claimedBy: 'Staff_Kamal',
    aiEnabled: false,
    createdAt: '25 mins ago',
    messages: [
      {
        id: 'm-201',
        authorName: 'NuwanK',
        authorRole: 'customer',
        content: '**Subject:** Mage VPS eke UFW firewall eka on karala SSH block una\n\nsudo ufw enable kalaata passe ssh port eken disconnect una. Dan connect wenna ba bro help ekak ona.',
        timestamp: '25 mins ago',
        detectedLang: 'singlish'
      },
      {
        id: 'm-202',
        authorName: 'HELZERX AI Support',
        authorRole: 'ai',
        content: `Ape side eken baluwama oyaage VPS eke UFW enable karaddi default deny policy eka apply wela wage penne (port 22 allow nokara ufw enable karama SSH connection eka drop wenawa).\n\nMe widiyata meka fix karaganna puluwan:\n\n1. **HELZERX Client Portal** ekata login wela **Services > VPS Management > VNC Console (NoVNC)** open karanna. VNC console eka firewall eka thibbath bypass wela directly screen eka load karanawa.\n2. Console eke root password eka gahala login wenna.\n3. Me commands run karanna:\n\`\`\`bash\nsudo ufw allow 22/tcp\nsudo ufw reload\n\`\`\`\n\nOyaata VNC eken login wenna amarunam mama ape on-duty human staff ekata notify karanna puluwan.`,
        timestamp: '24 mins ago',
        detectedLang: 'singlish',
        latencyMs: 178
      },
      {
        id: 'm-203',
        authorName: 'NuwanK',
        authorRole: 'customer',
        content: 'Mata VNC eken log wenna therenne na bro, staff kenekta hadala denna puluwanda?',
        timestamp: '20 mins ago',
        detectedLang: 'singlish'
      },
      {
        id: 'm-204',
        authorName: 'Staff_Kamal',
        authorRole: 'staff',
        content: 'Hello Nuwan, I am taking over this ticket. I have accessed the KVM management controller and opened port 22 in UFW. Please verify your SSH connection now.',
        timestamp: '15 mins ago',
        detectedLang: 'en'
      }
    ],
    internalNotes: [
      {
        id: 'in-2',
        author: 'Staff_Kamal',
        content: 'Customer locked out by ufw default deny. Resolved via host serial console without reboot.',
        timestamp: '14 mins ago'
      }
    ]
  }
];

export const KNOWLEDGE_DOCS = [
  {
    id: 'k-1',
    title: 'HELZERX Minecraft Paper & Purpur Optimization',
    category: 'minecraft',
    tags: ['paper', 'purpur', 'jvm', 'aikar', 'oom'],
    summary: 'Optimal Java 21 flags, GC pause tuning, and off-heap memory container allowances.',
    content: `For Minecraft Paper/Purpur instances on HELZERX Game Cloud:
1. Java Version Requirements:
   - Minecraft 1.12.2 - 1.16.4: Java 8 or Java 11.
   - Minecraft 1.17 - 1.20.4: Java 17 (Zulu or Temurin).
   - Minecraft 1.20.5 - 1.21+: Java 21 (Temurin 21 HotSpot).
2. Recommended Aikar's JVM Flags:
   \`\`\`bash
   -Xms{RAM}G -Xmx{RAM}G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1ReservePercent=20
   \`\`\`
3. Out of Memory (OOM) Errors:
   If Pterodactyl console shows "Killed process", ensure server startup allocation (-Xmx) leaves at least 1024MB for off-heap container overhead.`
  },
  {
    id: 'k-2',
    title: 'HELZERX Pterodactyl Wings Troubleshooting',
    category: 'technical',
    tags: ['pterodactyl', 'wings', 'docker', 'ssl'],
    summary: 'Resolving daemon offline states, EHOSTUNREACH, and Let\'s Encrypt expired certs.',
    content: `Common Pterodactyl Wings issues and step-by-step resolution:
1. Wings Service Status:
   Check service status: sudo systemctl status wings
   Inspect real-time logs: sudo journalctl -u wings -n 100 --no-pager
2. EHOSTUNREACH / Connection Refused:
   - Verify Wings is listening on port 8080: sudo ss -tulpn | grep wings
   - Check firewall rules: sudo ufw allow 8080/tcp
3. SSL Certificate Expiry / Certbot:
   If Wings logs report "certificate has expired":
   - Run: sudo certbot renew
   - Restart wings: sudo systemctl restart wings`
  },
  {
    id: 'k-3',
    title: 'HELZERX Cloudflare DNS & Minecraft Domain Linking',
    category: 'technical',
    tags: ['cloudflare', 'dns', 'srv', 'orange cloud'],
    summary: 'Setting up Grey Cloud DNS-Only records and SRV records for Minecraft and game servers.',
    content: `When connecting custom domains (e.g., play.mycommunity.com) to HELZERX servers:
1. Proxy Status (Orange Cloud vs Grey Cloud):
   - CRITICAL: Cloudflare's HTTP/HTTPS Proxy (Orange Cloud) ONLY forwards web traffic (ports 80, 443).
   - Raw game protocols (Minecraft TCP 25565) CANNOT pass through Cloudflare Orange Cloud without Cloudflare Spectrum.
   - You MUST set the DNS record to "DNS Only" (Grey Cloud).
2. Dedicated Port (Default 25565):
   - Type: A record
   - Name: play
   - Target: YOUR_SERVER_IP
   - Proxy: DNS only (Grey Cloud)
3. Non-Standard Port (SRV Record):
   - A Record: mc.domain.com -> SERVER_IP (Grey Cloud)
   - SRV Record: _minecraft._tcp.play -> Priority 0, Weight 5, Port {PORT}, Target mc.domain.com`
  },
  {
    id: 'k-4',
    title: 'HELZERX Dedicated Servers & Anti-DDoS Architecture',
    category: 'dedicated',
    tags: ['dedicated', 'ddos', 'corero', 'voxility', 'ipmi'],
    summary: '3.2 Tbps inline multi-tier DDoS mitigation, IPMI/iDRAC management, and hardware specs.',
    content: `1. Hardware Architecture:
   - AMD EPYC 7003/9004 Series & Intel Xeon Scalable Processors.
   - Enterprise NVMe PCIe 4.0 in RAID 1 / RAID 10 configuration.
   - Dual 10Gbps redundant uplinks with BGP Anycast routing.
2. Anti-DDoS Mitigation:
   - Multi-layer 3.2 Tbps mitigation capacity powered by inline Corero & Voxility scrubbing filters.
   - Automatic mitigation triggers in under 1 second without dropping TCP sessions.
   - Dedicated game query filters for Source Engine, RakNet, and Minecraft flood protection.`
  },
  {
    id: 'k-5',
    title: 'HELZERX Billing, Refund Policy & Service SLA',
    category: 'billing',
    tags: ['billing', 'refund', 'sla', 'guarantee'],
    summary: '7-day money-back guarantee, invoice grace periods, and payment methods.',
    content: `1. 7-Day Money-Back Guarantee:
   - Standard VPS and Game Hosting instances are eligible for a 100% full refund within 7 calendar days of first order.
   - Dedicated Bare Metal Servers and domain registrations are non-refundable due to physical provisioning costs.
2. Invoicing & Due Dates:
   - Invoices generate 7 days before service expiration.
   - Grace period: Servers remain online for 48 hours past due date before automatic suspension.`
  }
];

export const AUDIT_LOGS = [
  { id: '1', action: 'TICKET_CREATED', actor: 'AlexV', ticket: 'HZX-8429', details: 'Cat: Minecraft Hosting, Priority: HIGH', time: '10 mins ago' },
  { id: '2', action: 'AI_DIAGNOSTIC_GENERATED', actor: 'HELZERX AI', ticket: 'HZX-8429', details: 'Language: English, Tokens: 412, Latency: 142ms', time: '9 mins ago' },
  { id: '3', action: 'INTERNAL_NOTE_ADDED', actor: 'Staff_Devon', ticket: 'HZX-8429', details: 'Node memory check verified at 64%', time: '8 mins ago' },
  { id: '4', action: 'TICKET_CREATED', actor: 'NuwanK', ticket: 'HZX-3105', details: 'Cat: VPS Support, Priority: URGENT', time: '25 mins ago' },
  { id: '5', action: 'TICKET_ESCALATED', actor: 'NuwanK', ticket: 'HZX-3105', details: 'Reason: Customer requested human staff', time: '20 mins ago' },
  { id: '6', action: 'TICKET_CLAIMED', actor: 'Staff_Kamal', ticket: 'HZX-3105', details: 'Assigned to Staff_Kamal', time: '15 mins ago' },
  { id: '7', action: 'SECURITY_AUDIT_PASSED', actor: 'System', ticket: 'Global', details: 'All 18 automated test suites passing', time: '1 hour ago' }
];
