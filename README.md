# تفادي القنبلة | Tafadi Al-Qonbula

لعبة جماعية عربية لسطح المكتب مبنية بـ **Python 3.12** و**PySide6**. تعمل اللعبة محليًا دون قاعدة بيانات أو اتصال بالإنترنت، وتطبق القرارات المتزامنة، منع تعارض الوجهات، دورات القنبلة، الكشف بعد الجولة الثالثة، والاستبعاد حتى بقاء فائز واحد.

## PROJECT TREE

```text
tafadi-al-qonbula/
├── main.py
├── game.py
├── ui.py
├── assets.py
├── build.py
├── requirements.txt
├── assets/
│   ├── bomb.svg
│   ├── bomb.png              # يُنشأ من bomb.svg عند تجهيز الأصول
│   ├── app.ico               # يُنشأ من bomb.png عند تجهيز الأصول
│   ├── icons/                # Lucide SVG icons
│   └── sounds/               # ملفات WAV اختيارية
├── .github/workflows/build.yml
└── README.md
```

## التثبيت والتشغيل | Installation and Running

ثبّت Python 3.12 ثم نفّذ:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The game is offline-first. Optional WAV files may be placed in `assets/sounds/`; missing sound files do not stop the application.

## بناء EXE | Building the Windows executable

على Windows:

```bash
pip install -r requirements.txt
python build.py
```

ينتج البناء ملفًا داخل `dist/` باسم **تفادي القنبلة.exe** وبوضع Windows GUI دون نافذة Console. يعتمد `build.py` على PyInstaller، ينظف نواتج البناء السابقة، يتحقق من الموارد، ويضمّن مجلد `assets/`.

## GitHub Actions

يعمل الملف `.github/workflows/build.yml` على Windows عند الدفع إلى `main` أو `master` أو عند تشغيله يدويًا. يرفع الناتج كـ artifact باسم `tafadi-al-qonbula-windows`.

## الأصول والترخيص | Assets and Licensing

أيقونات الواجهة مأخوذة من **Lucide**، وهي مجموعة SVG مفتوحة المصدر مرخصة بموجب ISC، وتُستخدم هنا كملفات فعلية لا كرموز نصية أو Emoji. صورة القنبلة الأساسية هي ملف `bomb.svg` من Lucide، ويمكن استبدالها بأصل فني تجاري مرخص مع إبقاء الاسم نفسه. راجع [Lucide License](https://lucide.dev/license) و[Lucide repository](https://github.com/lucide-icons/lucide) قبل التوزيع التجاري، واحتفظ بنص الترخيص أو الإسناد المطلوب ضمن حزمة المنتج.

لا تستخدم اللعبة Emoji كأيقونات. ملف `assets/bomb.png` و`assets/app.ico` يجب أن يكونا موجودين عند التوزيع النهائي؛ إذا كانت بيئة البناء لا توفرهما، يمكن تشغيل اللعبة من SVG، لكن يجب تجهيز نسخ PNG/ICO قبل إصدار تجاري Windows.

## Gameplay

كل لاعب حي يختار سرًا: البقاء، العودة إلى موقعه الأصلي، أو أخذ موقع لاعب حي آخر. يجمع المحرك القرارات أولًا، ثم يتحقق منها، ثم يحل التعارضات، ثم يطبق النقل دفعة واحدة. الحركات الدائرية مثل A إلى B وB إلى C وC إلى A مسموحة، بينما الوجهة التي يطلبها أكثر من لاعب تلغي طلبات المتنافسين جميعًا. لا تتبع القنبلة اللاعب؛ بل ترتبط بموقع مستقل، ولا يتكرر موقعها في الدورة التالية عندما يتوفر موقع بديل.

## License

كود هذا المشروع مثال تطبيقي أصلي مخصص للتطوير التجاري من قبل مالكه، مع ضرورة احترام تراخيص الأصول الخارجية المذكورة أعلاه. لا تُضمّن أي أصل خارجي جديد دون مراجعة ترخيصه وإضافة الإسناد المطلوب.
