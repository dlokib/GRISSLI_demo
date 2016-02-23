from django.db import models

# Create your models here.


class Task(models.Model):
    timeshift = models.IntegerField(default = 0)
    url = models.CharField(max_length = 128, unique = True)

    def __str__(self):
        minutes, seconds = divmod(self.timeshift, 60)

        return "{0}:{1}, {2}".format(minutes, seconds, self.url)


class Codec(models.Model):
    name = models.CharField(max_length = 16)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length = 16, unique = True)

    def __str__(self):
        return self.name


class Result(models.Model):
    task = models.ForeignKey(Task)
    status = models.ForeignKey(Status, null = True)
    timestamp = models.IntegerField(default = 0)
    codec = models.ForeignKey(Codec, null = True)
    title = models.CharField(max_length = 64)
    header = models.CharField(max_length = 128)

    def __str__(self):
        name = 'Unknown'
        if self.codec:
            name = self.codec.name

        return str((name, self.title, self.header))

    def dictionary(self):
        return {
            'timestamp' : self.timestamp,
            'status' : self.status.name,
            'codec' : self.codec.name,
            'title' : self.title,
            'header' : self.header,
            'url' : self.task.url
        }
 