# Who's Next? | Sıradaki Kim?
A student picker | Bir öğrenci seçici

[English](#english) | [Türkçe](#turkce)

## Türkçe
Sıradaki Kim?, Pardus kullanan sınıf bilgisayarları ve tahtalar için hazırlanmış bir öğrenci seçme uygulamasıdır. Sınıf listesini PDF olarak yükleyip kolu çekerek rastgele öğrenci seçebilirsiniz.

### Özellikler

- PDF sınıf listesinden öğrenci okuma
- Kolu çekerek seçim yapılan arayüz
- Türkçe ve Ingilizce dil desteği
- Normal kullanıcılar için AppImage sürümü
- Sınıf tahtalarına kurulum için `install.sh`
- GitHub Releases üzerinden güncelleme paketi desteği

### AppImage Kullanımı

Root yetkisi gerektirmeden çalıştırmak için AppImage dosyasını kullanın:

```bash
chmod +x WhosNext-1.0.0-x86_64.AppImage
./WhosNext-1.0.0-x86_64.AppImage
```

AppImage sürümü kendi içinden güncelleme yapmaz. Yeni sürüm çıktığında GitHub Releases üzerinden yeni AppImage dosyasını indirmeniz gerekir.

### Sistem Kurulumu

Sınıf tahtalarına paylaşımlı kurulum yapmak için:

```bash
sudo ./install.sh
```

Bu kurulum:

- Uygulamayı `/opt/whos-next` altına kopyalar
- Sanal ortam oluşturur
- Kütüphaneleri kurar
- Mevcut kullanıcıları uygulama grubuna ekler
- Masaüstü kısayollarını mevcut ve yeni kullanıcılar için olusturur

### Güncelleme

Sürüm numarası `VERSION` dosyasından okunur.

Zip güncelleme paketi oluşturmak için:

```bash
./build_release_bundle.sh
```

AppImage oluşturmak için:

```bash
./build_appimage.sh
```

### Geliştirme Notu

*Bu proje okul kullanımına yönelik olarak hazırlandı ve geliştirme sürecinde AI desteği kullanıldı. Kod ve dağıtım akışının son hali manuel olarak düzenlendi ve dağıtım amacına göre uyarlandı.*

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

### Development Note

*This project was built for school use and was developed with AI assistance. The final code and release flow were manually cleaned up and adapted for real deployment.*
