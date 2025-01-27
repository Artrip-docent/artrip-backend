from django.db import models

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()  # 요청자의 ip 주소
    requested_at = models.DateTimeField(auto_now_add=True)  # 요청 시간
    title = models.CharField(max_length=255)  # 반환된 작품 이름
    artist = models.CharField(max_length=255)  # 반환된 작가 이름

    def __str__(self):
        return f"{self.artwork_name} by {self.artist} at {self.requested_at}"