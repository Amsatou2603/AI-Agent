import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Widget pour afficher un tableau de données
class DataTableWidget extends StatelessWidget {
  final List<Map<String, dynamic>> data;

  const DataTableWidget({
    super.key,
    required this.data,
  });

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) return const SizedBox.shrink();

    final columns = data.first.keys.toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Données',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: AppTheme.secondary,
              ),
        ),
        const SizedBox(height: AppTheme.paddingMedium),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0xFFE8EAED), width: 1),
            borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                headingRowColor: WidgetStateProperty.all(
                  AppTheme.secondary.withOpacity(0.1),
                ),
                columns: columns
                    .map(
                      (col) => DataColumn(
                        label: Text(
                          _capitalizeFirst(col),
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                            color: AppTheme.secondary,
                          ),
                        ),
                      ),
                    )
                    .toList(),
                rows: data
                    .map(
                      (row) => DataRow(
                        cells: columns
                            .map(
                              (col) => DataCell(
                                Text(
                                  row[col].toString(),
                                  style: const TextStyle(
                                    fontSize: 14,
                                    color: AppTheme.textPrimary,
                                  ),
                                ),
                              ),
                            )
                            .toList(),
                      ),
                    )
                    .toList(),
              ),
            ),
          ),
        ),
      ],
    );
  }

  String _capitalizeFirst(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }
}
