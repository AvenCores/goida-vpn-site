def get_vpn_configs():
    base_url = "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/"
    
    configs = []
    # Рекомендованные согласно README: 1, 6, 22, 23, 24, 25
    recommended_ids = [1, 6, 22, 23, 24, 25]
    
    for i in range(1, 27):
        configs.append({
            "id": i,
            "name": f"Config {i}.txt",
            "url": f"{base_url}{i}.txt",
            "is_recommended": i in recommended_ids,
            "is_sni": i == 26, # Обход SNI/CIDR
            "qr_link": f"https://github.com/AvenCores/goida-vpn-configs/blob/main/qr-codes/{i}.png"
        })

    return configs