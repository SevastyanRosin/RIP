from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Unit(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название", blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="default.png", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)

    phone = models.CharField(blank=True)

    def get_image(self):
        return self.image.url.replace("minio", "localhost", 1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        db_table = "units"


class Order(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True,
                              related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Сотрудник", null=True,
                                  related_name='moderator')

    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Приказ №" + str(self.pk)

    def get_units(self):
        return [
            setattr(item.unit, "value", item.value) or item.unit
            for item in UnitOrder.objects.filter(order=self)
        ]

    class Meta:
        verbose_name = "Приказ"
        verbose_name_plural = "Приказы"
        ordering = ('-date_formation',)
        db_table = "orders"


class UnitOrder(models.Model):
    unit = models.ForeignKey(Unit, models.DO_NOTHING, blank=True, null=True)
    order = models.ForeignKey(Order, models.DO_NOTHING, blank=True, null=True)
    value = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "unit_order"
        unique_together = ('unit', 'order')
