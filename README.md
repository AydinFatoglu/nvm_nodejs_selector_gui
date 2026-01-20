# NVM for Windows - No Admin Edition

Windows'ta Node.js versiyonlarını yönetmek için basit bir araç. Kurumsal ortamlarda veya admin yetkisi olmadan çalışır.

---

## Bu Nedir?

Node.js ile çalışırken farklı projeler farklı versiyonlar isteyebilir. Normalde NVM for Windows bunu symlink ile çözüyor ama her versiyon değişikliğinde admin şifresi soruyor. Özellikle şirket bilgisayarlarında bu çok can sıkıcı.

Bu araç aynı işi farklı bir yöntemle yapıyor. Symlink yerine PATH değişkeni üzerinden çalışıyor. Böylece versiyon değiştirirken admin yetkisine ihtiyaç duymuyor. GUI üzerinden istediğin versiyonu seç, yeni bir terminal aç ve kullanmaya başla.

---

## Nasıl Kullanılır?

İlk kurulum için `nvm_installer.exe` dosyasını çalıştır. Bu sadece bir kere gerekiyor ve ortam değişkenlerini ayarlıyor. Sonrasında terminalden `nvm install 20` gibi komutlarla istediğin Node versiyonlarını indir.

Versiyon değiştirmek istediğinde `nvm_gui.exe` dosyasını aç. Kurulu versiyonlar listede görünecek, istediğine tıkla ve "Set / Use" butonuna bas. Yeni bir terminal penceresi açtığında seçtiğin versiyon aktif olacak.

---

## Önemli Not

Terminalde `nvm use` komutunu kullanma çünkü o hala admin yetkisi istiyor. Onun yerine her zaman GUI aracını kullan. `nvm install` ve `nvm list` komutları normal çalışıyor, sadece `nvm use` yerine GUI tercih et.
