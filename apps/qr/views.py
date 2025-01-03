# qr/views.py
from django.http import HttpResponse, JsonResponse
from PIL import Image
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import logging
import pycountry
import phonenumbers
from rest_framework.request import Request

from rest_framework.views import APIView

from apps.qr.decorators import qr_swagger_decorator
from apps.qr.utils.qr_utils import (
    QRColorMasks,
    QRStyles,
    generate_url_qr,
    generate_email_qr,
    generate_text_qr,
    generate_phone_qr,
    generate_vcard_qr,
    generate_wifi_qr,
    generate_sms_qr,
    generate_bitcoin_qr,
    generate_whatsapp_qr,
    generate_mecard_qr,
    generate_event_qr,
    generate_geo_qr,
)

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class BaseQrView(APIView):
    def validate_common_params(self, request: Request):
        """공통 파라미터 검증"""
        try:
            style = request.data.get("style", "SQUARE_MODULE")
            fill_color = request.data.get("fill_color", "black")
            back_color = request.data.get("back_color", "white")
            color_mask = request.data.get("color_mask", "SOLID_FILL")
            embedded_image_ratio = float(request.data.get("embedded_image_ratio", 0.25))

            if not (0.1 <= embedded_image_ratio <= 0.5):
                raise ValueError("embedded_image_ratio must be between 0.1 and 0.5")

            try:
                style = QRStyles[style]
            except KeyError:
                logger.error(f"Invalid style parameter: {style}")
                raise ValueError(f"Invalid style. Valid options are: {', '.join(QRStyles.__members__.keys())}")

            try:
                color_mask = QRColorMasks[color_mask]
            except KeyError:
                logger.error(f"Invalid color_mask parameter: {color_mask}")
                raise ValueError(f"Invalid color mask. Valid options are: {', '.join(QRColorMasks.__members__.keys())}")

            return {
                "style": style,
                "fill_color": fill_color,
                "back_color": back_color,
                "color_mask": color_mask,
                "embedded_image_ratio": embedded_image_ratio
            }
        except Exception as e:
            logger.error(f"Parameter validation error: {str(e)}")
            raise ValueError(str(e))

    def process_embedded_image(self, request: Request):
        embedded_image = None
        if 'embedded_image' in request.FILES:
            try:
                image_file = request.FILES['embedded_image']
                embedded_image = Image.open(image_file)
            except Exception as e:
                raise ValueError("Invalid embedded image file.")
        return embedded_image

    def handle_qr_generation(self, request: Request, generator_func, required_params):
        """QR 코드 생성 템플릿 메서드"""
        try:
            # 요청 데이터 로깅
            logger.debug(f"Request data: {request.data}")

            # 1. 필요 파라미터 검증
            missing_params = [param for param in required_params if not request.data.get(param)]
            if missing_params:
                return JsonResponse(
                    {"detail": f"Missing required parameters: {', '.join(missing_params)}"},
                    status=400
                )

            # 2. 공통 파라미터
            try:
                common_params = self.validate_common_params(request)
            except ValueError as e:
                return JsonResponse({"detail": str(e)}, status=400)

            # 3. 임베드 이미지
            try:
                embedded_image = self.process_embedded_image(request)
            except ValueError as e:
                return JsonResponse({"detail": str(e)}, status=400)

            # 4. 요청 파라미터 준비
            generator_params = {k: request.data.get(k) for k in required_params}
            generator_params.update(common_params)
            generator_params['embedded_image'] = embedded_image

            # 파라미터 로깅
            logger.debug(f"Generator parameters: {generator_params}")

            # 5. QR 코드 생성
            qr_image = generator_func(**generator_params)

            if not qr_image:
                raise ValueError("Failed to generate QR code")

            # 6. 응답 생성
            response = HttpResponse(qr_image, content_type="image/png")
            response['Content-Length'] = len(qr_image)
            response['Content-Disposition'] = 'inline; filename="qr-code.png"'

            # 성공 로깅
            logger.info(f"Successfully generated QR code: {len(qr_image)} bytes")

            return response

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return JsonResponse({"detail": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error generating QR Code: {str(e)}")
            return JsonResponse(
                {"detail": "An unexpected error occurred while generating the QR Code."},
                status=500
            )

class QrVcardView(BaseQrView):
    @qr_swagger_decorator(
        "VCard QR Code",
        {
            "first_name": openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
            "vcard_mobile": openapi.Schema(type=openapi.TYPE_STRING, description='Mobile phone number'),
            "vcard_email": openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            "vcard_url": openapi.Schema(type=openapi.TYPE_STRING, description='Website URL'),
            "organization": openapi.Schema(type=openapi.TYPE_STRING, description='Organization'),
            "job_title": openapi.Schema(type=openapi.TYPE_STRING, description='Job title'),
            "fax": openapi.Schema(type=openapi.TYPE_STRING, description='Fax number'),
            "address": openapi.Schema(type=openapi.TYPE_STRING, description='Address'),
            "zip": openapi.Schema(type=openapi.TYPE_STRING, description='Zip code'),
            "country": openapi.Schema(type=openapi.TYPE_STRING, description='Country'),
            "note": openapi.Schema(type=openapi.TYPE_STRING, description='Note')
        }
    )
    def post(self, request):
        return self.handle_qr_generation(
            request,
            generate_vcard_qr,
            ["first_name", "last_name", "vcard_mobile", "vcard_email"]
        )


class QrUrlView(BaseQrView):
    @qr_swagger_decorator(
        "URL QR Code",
        {
            "url": openapi.Schema(type=openapi.TYPE_STRING, description='URL to encode in the QR Code'),
        }
    )
    def post(self, request: Request):
        return self.handle_qr_generation(request, generate_url_qr, ["url"])


class QrEmailView(BaseQrView):
    @qr_swagger_decorator(
        "Email QR Code",
        {
            "email": openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            "subject": openapi.Schema(type=openapi.TYPE_STRING, description='Subject'),
            "body": openapi.Schema(type=openapi.TYPE_STRING, description='Body'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(request, generate_email_qr, ["email"])


class QrTextView(BaseQrView):
    @qr_swagger_decorator(
        "Text QR Code",
        {
            "text": openapi.Schema(type=openapi.TYPE_STRING, description='Text to encode'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(request, generate_text_qr, ["text"])


class QrPhoneNumberView(BaseQrView):
    @qr_swagger_decorator(
        "Phone Number QR Code",
        {
            "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(request, generate_phone_qr, ["phone_number"])


class QrWifiView(BaseQrView):
    @qr_swagger_decorator(
        "WiFi QR Code",
        {
            "ssid": openapi.Schema(type=openapi.TYPE_STRING, description='Network SSID'),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description='Network password'),
            "encryption": openapi.Schema(type=openapi.TYPE_STRING, description='Encryption type (WEP, WPA, WPA2)'),
            "hidden": openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the network is hidden'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(request, generate_wifi_qr, ["ssid"])


class QrSmsView(BaseQrView):
    @qr_swagger_decorator(
        "SMS QR Code",
        {
            "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
            "message": openapi.Schema(type=openapi.TYPE_STRING, description='SMS message'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(request, generate_sms_qr, ["phone_number"])


class QrGeoView(BaseQrView):
    @qr_swagger_decorator(
        "Geolocation QR Code",
        {
            "latitude": openapi.Schema(type=openapi.TYPE_NUMBER, description='Latitude'),
            "longitude": openapi.Schema(type=openapi.TYPE_NUMBER, description='Longitude'),
            "query": openapi.Schema(type=openapi.TYPE_STRING, description='Query string'),
            "zoom": openapi.Schema(type=openapi.TYPE_INTEGER, description='Zoom level'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(
            request,
            generate_geo_qr,
            ["latitude", "longitude"]
        )


class QrEventView(BaseQrView):
    @qr_swagger_decorator(
        "Event QR Code",
        {
            "summary": openapi.Schema(type=openapi.TYPE_STRING, description='Event summary'),
            "start_date": openapi.Schema(type=openapi.TYPE_STRING, description='Start date (YYYYMMDD)'),
            "end_date": openapi.Schema(type=openapi.TYPE_STRING, description='End date (YYYYMMDD)'),
            "location": openapi.Schema(type=openapi.TYPE_STRING, description='Event location'),
            "description": openapi.Schema(type=openapi.TYPE_STRING, description='Event description'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(
            request,
            generate_event_qr,
            ["summary", "start_date", "end_date", "location", "description"]
        )


class QrMeCardView(BaseQrView):
    @qr_swagger_decorator(
        "MECARD QR Code",
        {
            "name": openapi.Schema(type=openapi.TYPE_STRING, description='Name of the contact'),
            "reading": openapi.Schema(type=openapi.TYPE_STRING, description='Phonetic reading of the name'),
            "tel": openapi.Schema(type=openapi.TYPE_STRING, description='Telephone number'),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            "memo": openapi.Schema(type=openapi.TYPE_STRING, description='Memo or note'),
            "birthday": openapi.Schema(type=openapi.TYPE_STRING, description='Birthday in YYYYMMDD format'),
            "address": openapi.Schema(type=openapi.TYPE_STRING, description='Address'),
            "url": openapi.Schema(type=openapi.TYPE_STRING, description='Website URL'),
            "nickname": openapi.Schema(type=openapi.TYPE_STRING, description='Nickname'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(
            request,
            generate_mecard_qr,
            ["name", "reading", "tel", "email"]
        )


class QrWhatsAppView(BaseQrView):
    @qr_swagger_decorator(
        "WhatsApp QR Code",
        {
            "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description='Recipient\'s phone number in international format'),
            "message": openapi.Schema(type=openapi.TYPE_STRING, description='Message to send'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(request, generate_whatsapp_qr, ["phone_number"])


class QrBitcoinView(BaseQrView):
    @qr_swagger_decorator(
        "Bitcoin Payment QR Code",
        {
            "address": openapi.Schema(type=openapi.TYPE_STRING, description='Bitcoin wallet address'),
            "amount": openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount in BTC'),
            "label": openapi.Schema(type=openapi.TYPE_STRING, description='Label for the payment'),
            "message": openapi.Schema(type=openapi.TYPE_STRING, description='Message or note'),
        }
    )
    def post(self, request):
        return self.handle_qr_generation(
            request, generate_bitcoin_qr, ["address", "amount", "label", "message"]
        )


## 테스트 뷰
class HelloWorldView(APIView):
    @swagger_auto_schema(
        operation_description="This is a test view",
        responses={200: openapi.Response("Hello World")},
    )
    def get(self, request):
        return HttpResponse("Hello World")


class HelloDjangoView(APIView):
    @swagger_auto_schema(
        operation_description="This is a test view",
        responses={200: openapi.Response("Hello Django")},
    )
    def post(self, request):
        return HttpResponse("Hello Django")