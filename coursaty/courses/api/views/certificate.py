# views/certificate.py

from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from coursaty.courses.api.serializers.certificate import CertificateSerializer
from coursaty.courses.models import Certificate


class CertificateVerifyView(APIView):
    def get(self, request, certificate_id):
        cert = Certificate.verify_certificate(certificate_id)
        if not cert:
            msg = "Invalid certificate ID."
            raise NotFound(msg)
        return Response(CertificateSerializer(cert).data)
