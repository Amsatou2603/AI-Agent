import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:agent_ia_flutter/main.dart';

void main() {
  testWidgets('App loads successfully', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const AgentIAApp());

    // Verify that the app title is displayed
    expect(find.text('Agent IA Sénégal'), findsOneWidget);
    
    // Verify that the warning banner is displayed
    expect(find.text('Données pédagogiques fictives — aucune donnée officielle'), findsOneWidget);
  });
}
