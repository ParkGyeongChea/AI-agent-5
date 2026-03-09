
# ==========================================================
# 1️⃣ 추천 API가 반환할 것처럼 생긴 구조 정의
# ==========================================================

recommend_mock = {
    "videos": [    # 여러 개의 영상을 담기 때문에 리스트 구조
        {
            "video_id" : "eGEg98j4JQw",
            "id": "1",  # 영상 고유 식별자 (나중에 summary API에서 사용)
            "title": "Growth Strategy Deep Dive",
            "channel": "Startup School",
            "duration": "2:00:00"
        },
        {
            "video_id" : "xkZMUX_oQX4",
            "id": "2",
            "title": "Startup Marketing 101 Startup Marketing 101 Startup Marketing 101 Startup Marketing 101 Marketing Lab Marketing Lab Marketing Lab Marketing Lab Marketing Lab Marketing Lab",
            "channel": "Marketing Lab Marketing Lab Marketing Lab Marketing Lab Marketing Lab Marketing Lab Marketing Lab Marketing Lab",
            "duration": "1:30:00"
        },
        {
            "video_id" : "hwjXVpfAqxM",
            "id": "3",
            "title": "Brand Positioning Explained",
            "channel": "Brand Master",
            "duration": "1:00:00"
        }
    ]
}
