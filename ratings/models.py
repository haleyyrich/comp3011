from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError

class Professor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Module(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    semester = models.IntegerField()
    professor = models.ManyToManyField(Professor)

    def __str__(self):
        return f"{self.name}: Year: {self.year}, Semester: {self.semester}"
    
class Rating(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, null=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.module.professor.filter(id=self.professor.id).exists():
            raise ValidationError(f"{self.professor.name} does not teach {self.module.name}")

    def save(self, *args, **kwargs):
        self.clean()  # 🔥 Enforce validation before saving
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Rating: {self.rating} - {self.professor.name} in {self.module.name}"