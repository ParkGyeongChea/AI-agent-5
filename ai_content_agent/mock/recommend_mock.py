"""
recommend_mock.py

이 파일은 백엔드 API가 아직 완성되지 않았기 때문에
추천 API를 대신할 가짜(Mock) 데이터를 제공한다

Mock 데이터를 사용하는 이유
1. 프론트엔드 개발을 먼저 진행할 수 있다
2. API 응답 형태를 미리 설계할 수 있다
3. 백엔드와 협업 시 데이터 계약(contract)을 명확히 할 수 있다

실무에서도 프론트 개발을 먼저 진행할 때
Mock 데이터를 사용한다
"""

# ==========================================================
# 1️⃣ 추천 API가 반환할 것처럼 생긴 구조 정의
# ==========================================================
# "우리가 나중에 받을 실제 API 응답 형태를 미리 설계하는 것"

# 리스트로 바로 만들지 않고 {} 감싸서 만드는 이유
# 1. 실제 API 응답 구조를 따르기 위해
# 2. 확장성을 위해
# 3. 데이터 의미를 명확히 하기 위해
# 4. 프론트 - 백엔드 계약을 미리 정의하기 위해
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
