from scapy.all import sniff, DNSQR

def process_dns_packet(packet):
    if packet.haslayer(DNSQR):
        # Lấy thông tin từ gói tin DNS
        dns_query = packet[DNSQR].qname.decode('utf-8')
        print(f"DNS Query: {dns_query}")

# Bắt các gói tin DNS
sniff(filter="udp port 53", prn=process_dns_packet)
