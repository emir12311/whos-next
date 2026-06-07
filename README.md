# Who's Next?

[Turkce](#turkce) | [English](#english)

## Turkce

Who's Next?, Pardus kullanan sinif bilgisayarlari ve tahtalar icin hazirlanmis bir ogrenci secme uygulamasidir. Sinif listesini PDF olarak yukleyip kolu cekerek rastgele ogrenci secebilirsiniz.

### Ozellikler

- PDF sinif listesinden ogrenci okuma
- Kolu cekerek secim yapilan arayuz
- Turkce ve Ingilizce dil destegi
- Normal kullanicilar icin AppImage surumu
- Sinif bilgisayarlarina kurulum icin `install.sh`
- GitHub Releases uzerinden guncelleme paketi destegi

### AppImage Kullanimi

Root yetkisi gerektirmeden calistirmak icin AppImage dosyasini kullanin:

```bash
chmod +x WhosNext-1.0.0-x86_64.AppImage
./WhosNext-1.0.0-x86_64.AppImage
```

AppImage surumu kendi icinden guncelleme yapmaz. Yeni surum ciktiginda GitHub Releases uzerinden yeni AppImage dosyasini indirmeniz gerekir.

### Sistem Kurulumu

Sinif bilgisayarina paylasimli kurulum yapmak icin:

```bash
sudo ./install.sh
```

Bu kurulum:

- uygulamayi `/opt/whos-next` altina kopyalar
- sanal ortam olusturur
- bagimliliklari kurar
- mevcut kullanicilari uygulama grubuna ekler
- masaustu kisayollarini mevcut ve yeni kullanicilar icin olusturur

### Guncelleme ve Release

Surum numarasi `VERSION` dosyasindan okunur.

Zip guncelleme paketi olusturmak icin:

```bash
./build_release_bundle.sh
```

AppImage olusturmak icin:

```bash
./build_appimage.sh
```

GitHub Releases icin yuklenecek dosyalar:

- `dist/whos-next.zip`
- `dist/WhosNext-<version>-x86_64.AppImage`

### Gelistirme Notu

Bu proje okul kullanimina yonelik olarak hazirlandi ve gelistirme surecinde yogun AI destegi kullanildi. Kod ve dagitim akisinin son hali manuel olarak duzenlendi ve dagitim amacina gore uyarlandi.

## English

Who's Next? is a classroom student picker built for Pardus-based school computers and boards. You load a class-list PDF, pull the lever, and the app randomly selects a student.

### Features

- Reads students from class-list PDFs
- Lever-based picker interface
- Turkish and English language support
- AppImage build for normal users
- `install.sh` for shared classroom installation
- GitHub Releases zip update support

### AppImage Usage

Use the AppImage if you want to run the app without root installation:

```bash
chmod +x WhosNext-1.0.0-x86_64.AppImage
./WhosNext-1.0.0-x86_64.AppImage
```

The AppImage build does not self-update. When a new version is released, download the new AppImage from GitHub Releases.

### System Installation

To install it on a shared classroom machine:

```bash
sudo ./install.sh
```

This installer:

- copies the app into `/opt/whos-next`
- creates a virtual environment
- installs dependencies
- adds existing users to the app group
- creates desktop shortcuts for existing and future users

### Updates and Releases

The version number is read from the `VERSION` file.

To build the zip update bundle:

```bash
./build_release_bundle.sh
```

To build the AppImage:

```bash
./build_appimage.sh
```

Files to upload to GitHub Releases:

- `dist/whos-next.zip`
- `dist/WhosNext-<version>-x86_64.AppImage`

### Development Note

This project was built for school use and was developed with heavy AI assistance. The final code and release flow were manually cleaned up and adapted for real deployment.
