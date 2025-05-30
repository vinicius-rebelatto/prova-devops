FROM php:8.2-apache

WORKDIR /var/www/html

COPY index.php .

RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli

EXPOSE 80

CMD ["apache2-foreground"]