# Perl Test: Radius Accounting

Script CGI Perl untuk upload file radius accounting, proses simpan ke database
lalu menampilkan hasilnya.

## Requirement

Membutuhkan program & modul2 berikut:

 * Perl min v5.14.2
 * MySQL 5.x
 * Apache 2.2.x
 * HTML::Template
 * DBH::mysql

## Instalasi

Untuk menjalankan aplikasi ini:

1. ekstrak folder di bawah folder `cgi-bin`
2. buat symbolic link dari folder `assets` ke `htdocs` dengan nama `radtest-assets` (bisa
disesuaikan dengan variable `asset_url` di masing2 cgi)
3. pastikan folder `uploads` bisa ditulis oleh web server
4. sesuaikan konfigurasi database pada `config.pl`