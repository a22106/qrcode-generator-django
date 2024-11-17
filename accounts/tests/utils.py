from django.conf import settings
from core.supabase import supabase
import logging

logger = logging.getLogger(__name__)

TEST_USER_EMAIL = "test_user@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

def create_test_user():
    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "options": {
                    "data": {
                        "email": TEST_USER_EMAIL,
                    },
                    "email_redirect_to": f"{settings.SITE_URL}/",
                },
            }
        )
        user_id = auth_response.user.id
        logger.info(f"테스트 사용자 생성: {TEST_USER_EMAIL}")
        return user_id
    except Exception as e:
        logger.error(f"테스트 사용자 생성 실패: {e}")
        return None

def delete_test_user(user_id):
    try:
        supabase.auth.admin.delete_user(user_id)
        logger.info(f"테스트 사용자 삭제: {TEST_USER_EMAIL}")
    except Exception as e:
        logger.error(f"테스트 사용자 삭제 실패: {e}")