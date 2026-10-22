import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/data/latest.dart' as tzdata;
import 'package:timezone/timezone.dart' as tz;

const blue = Color(0xFF3AA6E0);
const paleBlue = Color(0xFFEAF6FD);
const disclaimer =
    'HealthMate gives general health information only. It does not replace a doctor and cannot diagnose conditions or prescribe medicine.';

final notifier = FlutterLocalNotificationsPlugin();

// ---------- storage (on-device; swap for Firebase/Firestore if you want cloud sync) ----------
Future<List<Map<String, dynamic>>> load(String k) async {
  final p = await SharedPreferences.getInstance();
  return (jsonDecode(p.getString(k) ?? '[]') as List).cast<Map<String, dynamic>>();
}

Future<void> save(String k, List l) async =>
    (await SharedPreferences.getInstance()).setString(k, jsonEncode(l));

// ---------- reminders ----------
Future<void> scheduleDaily(int id, String name, TimeOfDay t) async {
  final now = tz.TZDateTime.now(tz.local);
  var when = tz.TZDateTime(tz.local, now.year, now.month, now.day, t.hour, t.minute);
  if (when.isBefore(now)) when = when.add(const Duration(days: 1));
  await notifier.zonedSchedule(
    id,
    'Medicine reminder',
    'Time to take $name',
    when,
    const NotificationDetails(
      android: AndroidNotificationDetails('meds', 'Medicine reminders',
          importance: Importance.high, priority: Priority.high),
      iOS: DarwinNotificationDetails(),
    ),
    androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
    uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
    matchDateTimeComponents: DateTimeComponents.time,
  );
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  tzdata.initializeTimeZones();
  try {
    tz.setLocalLocation(tz.getLocation(await FlutterTimezone.getLocalTimezone()));
  } catch (_) {}
  await notifier.initialize(const InitializationSettings(
    android: AndroidInitializationSettings('@mipmap/ic_launcher'),
    iOS: DarwinInitializationSettings(),
  ));
  await notifier
      .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
      ?.requestNotificationsPermission();
  runApp(const HealthMate());
}

class HealthMate extends StatelessWidget {
  const HealthMate({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'HealthMate',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(seedColor: blue, surface: Colors.white),
          scaffoldBackgroundColor: Colors.white,
          appBarTheme: const AppBarTheme(backgroundColor: paleBlue, foregroundColor: Color(0xFF14506E)),
          cardTheme: const CardTheme(color: paleBlue, elevation: 0),
          textTheme: const TextTheme(bodyMedium: TextStyle(fontSize: 16, height: 1.4)),
        ),
        home: const Home(),
      );
}

Widget page(String title, Widget body, {Widget? fab}) => Scaffold(
      appBar: AppBar(title: Text(title)),
      body: SafeArea(child: body),
      floatingActionButton: fab,
    );

Widget note() => Container(
      margin: const EdgeInsets.all(12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: const Color(0xFFFFF8E1), borderRadius: BorderRadius.circular(12)),
      child: const Row(children: [
        Icon(Icons.info_outline, color: Colors.amber),
        SizedBox(width: 10),
        Expanded(child: Text(disclaimer, style: TextStyle(fontSize: 13))),
      ]),
    );

// ---------- Home ----------
class Home extends StatelessWidget {
  const Home({super.key});
  @override
  Widget build(BuildContext context) {
    final items = <(String, IconData, Widget)>[
      ('Symptom Checker', Icons.search, const SymptomPage()),
      ('Health Tips', Icons.favorite_outline, const TipsPage()),
      ('Medicine Reminder', Icons.medication_outlined, const MedsPage()),
      ('Doctors & Clinics', Icons.local_hospital_outlined, const DoctorsPage()),
      ('Health History', Icons.history, const HistoryPage()),
      ('Emergency Help', Icons.warning_amber_rounded, const EmergencyPage()),
    ];
    return Scaffold(
      body: SafeArea(
        child: ListView(padding: const EdgeInsets.all(16), children: [
          const SizedBox(height: 8),
          const Text('Hello, welcome to', style: TextStyle(fontSize: 18, color: Colors.black54)),
          const Text('HealthMate 💙',
              style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF14506E))),
          const SizedBox(height: 4),
          const Text('Learn about common health problems and look after yourself, one day at a time.'),
          const SizedBox(height: 16),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            children: [
              for (final i in items)
                InkWell(
                  borderRadius: BorderRadius.circular(16),
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => i.$3)),
                  child: Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    color: i.$1 == 'Emergency Help' ? const Color(0xFFFFEBEE) : paleBlue,
                    child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                      Icon(i.$2, size: 40, color: i.$1 == 'Emergency Help' ? Colors.red : blue),
                      const SizedBox(height: 8),
                      Text(i.$1, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.w600)),
                    ]),
                  ),
                ),
            ],
          ),
          note(),
        ]),
      ),
    );
  }
}

// ---------- Symptom checker ----------
const symptomInfo = <String, Map<String, String>>{
  'headache': {
    'causes': 'Tension, dehydration, lack of sleep, eye strain, stress, migraine.',
    'care': 'Rest, drink water, reduce screen time. See a doctor if it is sudden and severe, or keeps returning.'
  },
  'fever': {
    'causes': 'Common infections such as flu or cold, stomach infections, other illnesses.',
    'care': 'Rest and drink fluids. See a doctor if it lasts more than 3 days, is very high, or comes with a stiff neck or rash.'
  },
  'cough': {
    'causes': 'Cold, flu, allergies, throat irritation, asthma, smoking.',
    'care': 'Warm fluids and rest. See a doctor if it lasts over 2–3 weeks, or you cough blood or struggle to breathe.'
  },
  'sore throat': {
    'causes': 'Viral infections, strep throat, dry air, allergies.',
    'care': 'Warm drinks, rest your voice. See a doctor if it lasts over a week or makes swallowing very hard.'
  },
  'stomach pain': {
    'causes': 'Indigestion, gas, food poisoning, constipation, stomach infection.',
    'care': 'Small light meals, fluids. Seek care if pain is severe, constant, or comes with vomiting blood or high fever.'
  },
  'fatigue': {
    'causes': 'Poor sleep, stress, low iron, thyroid issues, infections, low activity.',
    'care': 'Review sleep and diet. See a doctor if tiredness lasts for weeks without a clear reason.'
  },
  'nausea': {
    'causes': 'Stomach bug, food poisoning, motion sickness, migraine, pregnancy.',
    'care': 'Sip fluids slowly, eat bland food. Seek care if you cannot keep fluids down for a day.'
  },
};

class SymptomPage extends StatefulWidget {
  const SymptomPage({super.key});
  @override
  State<SymptomPage> createState() => _SymptomPageState();
}

class _SymptomPageState extends State<SymptomPage> {
  final c = TextEditingController();
  List<String> found = [];

  void check() {
    final t = c.text.toLowerCase();
    setState(() => found = symptomInfo.keys.where(t.contains).toList());
  }

  Future<void> saveEntry() async {
    final h = await load('history');
    h.insert(0, {'date': DateTime.now().toIso8601String(), 'text': c.text.trim()});
    await save('history', h);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Saved to Health History')));
    }
  }

  @override
  Widget build(BuildContext context) => page(
        'Symptom Checker',
        ListView(padding: const EdgeInsets.all(16), children: [
          TextField(
            controller: c,
            decoration: const InputDecoration(
                labelText: 'Describe your symptoms (e.g. fever and cough)', border: OutlineInputBorder()),
            maxLines: 2,
          ),
          Wrap(spacing: 8, children: [
            for (final s in symptomInfo.keys)
              ActionChip(
                  label: Text(s),
                  onPressed: () {
                    c.text = c.text.isEmpty ? s : '${c.text}, $s';
                    check();
                  }),
          ]),
          const SizedBox(height: 8),
          Row(children: [
            Expanded(child: FilledButton(onPressed: check, child: const Text('Show general information'))),
            const SizedBox(width: 8),
            OutlinedButton(onPressed: c.text.trim().isEmpty ? null : saveEntry, child: const Text('Save')),
          ]),
          const SizedBox(height: 12),
          if (found.isEmpty && c.text.isNotEmpty)
            const Text('No match in our small guide. If you are worried, please talk to a doctor or pharmacist.'),
          for (final s in found)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(s[0].toUpperCase() + s.substring(1),
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Text('Common causes: ${symptomInfo[s]!['causes']}'),
                  const SizedBox(height: 6),
                  Text('General advice: ${symptomInfo[s]!['care']}'),
                ]),
              ),
            ),
          note(),
        ]),
      );
}

// ---------- Tips ----------
class TipsPage extends StatelessWidget {
  const TipsPage({super.key});
  @override
  Widget build(BuildContext context) {
    const tips = [
      (Icons.restaurant, 'Healthy eating', 'Fill half your plate with vegetables and fruit, choose whole grains, and limit sugary drinks and fried food.'),
      (Icons.directions_run, 'Exercise', 'Aim for about 30 minutes of movement most days, such as brisk walking. Start slowly and build up.'),
      (Icons.bedtime_outlined, 'Sleep', 'Most adults need 7–9 hours. Keep regular sleep times and avoid screens before bed.'),
      (Icons.clean_hands, 'Hygiene', 'Wash hands with soap for 20 seconds before eating and after using the toilet. Brush teeth twice a day.'),
      (Icons.water_drop_outlined, 'Hydration', 'Drink water regularly through the day, especially in hot weather.'),
    ];
    return page(
      'Health Tips',
      ListView(padding: const EdgeInsets.all(16), children: [
        for (final t in tips)
          Card(
            child: ListTile(
              leading: Icon(t.$1, color: blue, size: 32),
              title: Text(t.$2, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(t.$3),
            ),
          ),
      ]),
    );
  }
}

// ---------- Medicine reminders ----------
class MedsPage extends StatefulWidget {
  const MedsPage({super.key});
  @override
  State<MedsPage> createState() => _MedsPageState();
}

class _MedsPageState extends State<MedsPage> {
  List<Map<String, dynamic>> meds = [];
  @override
  void initState() {
    super.initState();
    load('meds').then((m) => setState(() => meds = m));
  }

  Future<void> add() async {
    final name = TextEditingController();
    final time = await showDialog<TimeOfDay>(
      context: context,
      builder: (ctx) {
        TimeOfDay t = const TimeOfDay(hour: 8, minute: 0);
        return StatefulBuilder(
          builder: (ctx, set) => AlertDialog(
            title: const Text('Add medicine'),
            content: Column(mainAxisSize: MainAxisSize.min, children: [
              TextField(controller: name, decoration: const InputDecoration(labelText: 'Medicine name & dose as on your label')),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                icon: const Icon(Icons.alarm),
                label: Text('Daily at ${t.format(ctx)}'),
                onPressed: () async {
                  final p = await showTimePicker(context: ctx, initialTime: t);
                  if (p != null) set(() => t = p);
                },
              ),
            ]),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
              FilledButton(onPressed: () => Navigator.pop(ctx, t), child: const Text('Save')),
            ],
          ),
        );
      },
    );
    if (time == null || name.text.trim().isEmpty) return;
    final id = DateTime.now().millisecondsSinceEpoch % 1000000;
    meds.add({'id': id, 'name': name.text.trim(), 'h': time.hour, 'm': time.minute});
    await save('meds', meds);
    await scheduleDaily(id, name.text.trim(), time);
    setState(() {});
  }

  @override
  Widget build(BuildContext context) => page(
        'Medicine Reminder',
        meds.isEmpty
            ? const Center(child: Text('No medicines yet. Tap + to add one.'))
            : ListView(padding: const EdgeInsets.all(16), children: [
                for (final m in meds)
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.medication, color: blue),
                      title: Text(m['name']),
                      subtitle: Text('Daily at ${TimeOfDay(hour: m['h'], minute: m['m']).format(context)}'),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete_outline),
                        onPressed: () async {
                          await notifier.cancel(m['id']);
                          meds.remove(m);
                          await save('meds', meds);
                          setState(() {});
                        },
                      ),
                    ),
                  ),
                note(),
              ]),
        fab: FloatingActionButton(onPressed: add, child: const Icon(Icons.add)),
      );
}

// ---------- Doctors (sample data: replace with your own list or a Firestore collection) ----------
class DoctorsPage extends StatelessWidget {
  const DoctorsPage({super.key});
  @override
  Widget build(BuildContext context) {
    const docs = [
      ('Dr. Sample Khan', 'General Physician', 'City Care Clinic · Mon–Sat, 9am–5pm'),
      ('Dr. Sample Ali', 'Pediatrician', 'Family Health Center · Mon–Fri, 10am–4pm'),
      ('Dr. Sample Ahmed', 'Dentist', 'Smile Dental Clinic · Tue–Sun, 11am–7pm'),
      ('Dr. Sample Noor', 'Gynecologist', 'Women’s Care Hospital · Mon–Sat, 9am–2pm'),
    ];
    return page(
      'Doctors & Clinics',
      ListView(padding: const EdgeInsets.all(16), children: [
        const Text('Sample listings. Replace with real doctors and clinics in your area.', style: TextStyle(color: Colors.black54)),
        const SizedBox(height: 8),
        for (final d in docs)
          Card(
            child: ListTile(
              leading: const CircleAvatar(backgroundColor: blue, child: Icon(Icons.person, color: Colors.white)),
              title: Text(d.$1, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('${d.$2}\n${d.$3}'),
              isThreeLine: true,
            ),
          ),
      ]),
    );
  }
}

// ---------- History ----------
class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});
  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  List<Map<String, dynamic>> h = [];
  @override
  void initState() {
    super.initState();
    load('history').then((v) => setState(() => h = v));
  }

  @override
  Widget build(BuildContext context) => page(
        'Health History',
        h.isEmpty
            ? const Center(child: Text('No records yet. Save symptoms from the Symptom Checker.'))
            : ListView(padding: const EdgeInsets.all(16), children: [
                for (final e in h)
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.event_note, color: blue),
                      title: Text(e['text']),
                      subtitle: Text(DateTime.parse(e['date']).toLocal().toString().substring(0, 16)),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete_outline),
                        onPressed: () async {
                          h.remove(e);
                          await save('history', h);
                          setState(() {});
                        },
                      ),
                    ),
                  ),
              ]),
      );
}

// ---------- Emergency ----------
class EmergencyPage extends StatelessWidget {
  const EmergencyPage({super.key});
  @override
  Widget build(BuildContext context) {
    const signs = [
      'Chest pain or pressure',
      'Difficulty breathing',
      'Sudden weakness, face drooping, or slurred speech',
      'Severe bleeding that will not stop',
      'Fainting or loss of consciousness',
      'Seizure',
      'Sudden severe headache or confusion',
      'Severe allergic reaction (swelling of face or throat)',
      'Thoughts of harming yourself',
    ];
    return page(
      'Emergency Help',
      ListView(padding: const EdgeInsets.all(16), children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(color: const Color(0xFFFFEBEE), borderRadius: BorderRadius.circular(16)),
          child: const Text(
            'If you or someone else has any of these warning signs, call your local emergency number or go to the nearest hospital right away. Do not wait.',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
        ),
        const SizedBox(height: 12),
        for (final s in signs)
          ListTile(leading: const Icon(Icons.warning_amber_rounded, color: Colors.red), title: Text(s)),
        note(),
      ]),
    );
  }
}
