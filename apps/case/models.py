from django.db import models
import datetime
from django.utils.text import slugify
import transactions.service as trans_service
from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
import core.helper as hlp
# Create your models here.

class Client(models.Model):
    first_name = models.CharField(max_length=20, verbose_name='Ad')
    last_name = models.CharField(max_length=20, verbose_name='Soyad')
    phone = models.CharField(max_length=20, blank=True,null=True, verbose_name='Telefon')
    address = models.CharField(max_length=20, blank=True,null=True,verbose_name='Adres')
    email = models.CharField(max_length=50,blank=True,null=True,verbose_name='Email')
    city = models.ForeignKey('core.City', null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="clients", verbose_name="İl")
    district = models.ForeignKey('core.District', null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="clients", verbose_name="İlçe")
    description = models.TextField(null=True, blank=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        db_table = "client"

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def _generate_unique_slug(self):
        unique_slug = slugify(self.full_name)
        num = 1
        while Client.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(unique_slug, num)
            num += 1
        return unique_slug

    def __str__(self):
        return self.full_name

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def get_stats(self):
        return trans_service.get_stats_client(instance=self)

    def get_cname(self):
        class_name = 'Client'
        return class_name


class Partner(models.Model):
    LWYR = 1
    MR = 2
    MRS = 3
    OTHER = 3

    ALIAS = (
        (LWYR, "Avukat"),
        (MR, "Bay"),
        (MRS, "Bayan"),
        (OTHER, "Diğer"),
    )

    first_name = models.CharField(max_length=20, verbose_name='Ad')
    last_name = models.CharField(max_length=20, verbose_name='Soyad')
    alias = models.PositiveSmallIntegerField(choices=ALIAS,null=True,blank=True, verbose_name="Ünvan")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon')
    address = models.CharField(max_length=20, blank=True, null=True, verbose_name='Adres')
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name='Email')
    city = models.ForeignKey('core.City', null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="partners", verbose_name="İl")
    district = models.ForeignKey('core.District', null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="partners", verbose_name="İlçe")
    description = models.TextField(null=True, blank=True, verbose_name="Açıklama")


    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        db_table = "Partner"

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.full_name

    def _generate_unique_slug(self):
        unique_slug = slugify(self.full_name)
        num = 1
        while Partner.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(unique_slug, num)
            num += 1
        return unique_slug

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def get_stats(self):
        return trans_service.get_stats_partner(instance=self)

    def get_cname(self):
        class_name = 'Partner'
        return class_name




class Partnership(models.Model):
    partner = models.ForeignKey('case.Partner', on_delete=models.CASCADE,
                             related_name="partnerships", verbose_name="Ortaklık")
    case = models.ForeignKey('case.Case', null=True, blank=True, on_delete=models.CASCADE,
                             related_name="partnerships", verbose_name="Dosya")
    share = models.PositiveSmallIntegerField(null=True, blank=True,default=0, verbose_name="Hisse Yüzdesi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partnership"


class Status(models.Model):
    title = models.CharField(max_length=40, verbose_name='Başlık')
    color = models.CharField(max_length=10, verbose_name='Renk')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "status"

    def __str__(self):
        return self.title



class Case(models.Model):
    OPEN = 1
    CLOSE = 2
    IST = 3
    YAR = 4
    DERD = 5
    HT_OLUMLU = 6
    HT_OLUMSUZ = 7

    STATUS = (
        (OPEN, "Açık"),
        (CLOSE, "Olumsuz"),
        (IST, "İstinaf"),
        (YAR, "Yargıtay"),
        (DERD, "Derdest"),
        (HT_OLUMLU, "Hitam Olumlu"),
        (HT_OLUMSUZ, "Hitam Olumsuz"),
    )

    title = models.CharField(max_length=60, verbose_name='Başlık')
    case_id = models.CharField(max_length=60, null=True, blank=True, verbose_name='Dosya Numarası')
    date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)
    partner = models.ManyToManyField(Partner,related_name='cases', verbose_name="Ortak")
    client = models.ManyToManyField(Client, related_name='cases', verbose_name="Müvekkil")
    slug = models.SlugField(max_length=200, unique=True)
    city = models.ForeignKey('core.City', null=True, blank=True, on_delete=models.SET_NULL, related_name="instructor_city",verbose_name="İl")
    district = models.ForeignKey('core.District', null=True, blank=True, on_delete=models.SET_NULL, related_name="instructor_district",verbose_name="İlçe")
    status = models.PositiveSmallIntegerField(choices=STATUS,null=True,blank=True, verbose_name="Durum")
    expense = models.ManyToManyField('expense.Expense',null=True, blank=True, related_name='cases', verbose_name='Gelir-Gider')


    class Meta:
        db_table = "case"

    def __str__(self):
        return self.title

    def _generate_unique_slug(self):
        unique_slug = slugify(self.title)
        num = 1
        while Partner.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(unique_slug, num)
            num += 1
        return unique_slug

    def save(self,*args,**kwargs):
        if not self.date:
            self.date = datetime.date.today()
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def get_stats(self):
        return trans_service.get_stats_case(instance=self)

    def get_cname(self):
        class_name = 'Case'
        return class_name



