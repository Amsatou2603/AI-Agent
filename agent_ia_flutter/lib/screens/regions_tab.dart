import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class RegionsTab extends StatefulWidget {
  final Function(String) onQuestionSelected;

  const RegionsTab({
    super.key,
    required this.onQuestionSelected,
  });

  @override
  State<RegionsTab> createState() => _RegionsTabState();
}

class _RegionsTabState extends State<RegionsTab> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = "";

  // 14 Régions du Sénégal avec données 2024
  final List<Map<String, dynamic>> _allRegions = [
    {"name": "Dakar", "pop": "3.9M", "scol": "82.4%", "flag": "Capitale", "color": Color(0xFF008751)},
    {"name": "Thiès", "pop": "2.1M", "scol": "76.8%", "flag": null, "color": Color(0xFF2D6A4F)},
    {"name": "Diourbel", "pop": "1.8M", "scol": "58.9%", "flag": null, "color": Color(0xFF40916C)},
    {"name": "Kaolack", "pop": "1.3M", "scol": "62.1%", "flag": null, "color": Color(0xFF52B788)},
    {"name": "Saint-Louis", "pop": "1.2M", "scol": "69.5%", "flag": null, "color": Color(0xFF74C69D)},
    {"name": "Louga", "pop": "1.1M", "scol": "64.7%", "flag": null, "color": Color(0xFF95D5B2)},
    {"name": "Tambacounda", "pop": "0.9M", "scol": "55.3%", "flag": null, "color": Color(0xFFB7E4C7)},
    {"name": "Fatick", "pop": "0.9M", "scol": "68.2%", "flag": null, "color": Color(0xFFD8F3DC)},
    {"name": "Kolda", "pop": "0.8M", "scol": "60.5%", "flag": null, "color": Color(0xFF008751)},
    {"name": "Matam", "pop": "0.8M", "scol": "56.8%", "flag": null, "color": Color(0xFF2D6A4F)},
    {"name": "Kaffrine", "pop": "0.7M", "scol": "57.1%", "flag": null, "color": Color(0xFF40916C)},
    {"name": "Ziguinchor", "pop": "0.6M", "scol": "74.2%", "flag": null, "color": Color(0xFF52B788)},
    {"name": "Sédhiou", "pop": "0.6M", "scol": "59.4%", "flag": null, "color": Color(0xFF74C69D)},
    {"name": "Kédougou", "pop": "0.2M", "scol": "61.2%", "flag": null, "color": Color(0xFF95D5B2)},
  ];

  List<Map<String, dynamic>> get _filteredRegions {
    if (_searchQuery.isEmpty) return _allRegions;
    return _allRegions
        .where((r) => r['name'].toString().toLowerCase().contains(_searchQuery.toLowerCase()))
        .toList();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Title block
        Padding(
          padding: const EdgeInsets.only(
            left: AppTheme.paddingLarge,
            right: AppTheme.paddingLarge,
            top: AppTheme.paddingLarge,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: AppTheme.paddingMedium),
              const Text(
                'Statistiques Régionales',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.primary,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Explorez les indicateurs clés des 14 régions du Sénégal.',
                style: TextStyle(
                  fontSize: 13,
                  color: AppTheme.textSecondary,
                ),
              ),
              const SizedBox(height: 16),
              
              // Search input
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Rechercher une région...',
                  prefixIcon: const Icon(Icons.search_rounded, color: AppTheme.textTertiary),
                  contentPadding: const EdgeInsets.symmetric(vertical: 12),
                  fillColor: Colors.white,
                  filled: true,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(
                      color: AppTheme.textTertiary.withOpacity(0.15),
                    ),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(
                      color: AppTheme.textTertiary.withOpacity(0.15),
                    ),
                  ),
                ),
                onChanged: (val) {
                  setState(() {
                    _searchQuery = val;
                  });
                },
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
        
        // Regions Grid list
        Expanded(
          child: _filteredRegions.isEmpty
              ? _buildEmptySearch()
              : GridView.builder(
                  padding: const EdgeInsets.all(AppTheme.paddingLarge),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 14,
                    mainAxisSpacing: 14,
                    childAspectRatio: 0.88,
                  ),
                  itemCount: _filteredRegions.length,
                  itemBuilder: (context, idx) {
                    final region = _filteredRegions[idx];
                    return _buildRegionCard(region);
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildEmptySearch() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off_rounded,
            size: 48,
            color: AppTheme.textTertiary.withOpacity(0.5),
          ),
          const SizedBox(height: 16),
          const Text(
            'Aucune région trouvée',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: AppTheme.textSecondary,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Essayez une autre recherche.',
            style: TextStyle(
              fontSize: 12,
              color: AppTheme.textTertiary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRegionCard(Map<String, dynamic> region) {
    final bool hasFlag = region['flag'] != null;
    
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: AppTheme.shadowLight,
        border: Border.all(color: Colors.black.withOpacity(0.04)),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Image area representation
            Container(
              height: 54,
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    region['color'] as Color,
                    (region['color'] as Color).withOpacity(0.8),
                  ],
                ),
              ),
              child: Stack(
                children: [
                  Positioned(
                    right: -10,
                    bottom: -10,
                    child: Icon(
                      Icons.map_rounded,
                      size: 60,
                      color: Colors.white.withOpacity(0.12),
                    ),
                  ),
                  if (hasFlag)
                    Positioned(
                      bottom: 8,
                      left: 12,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.primary,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          region['flag'].toString().toUpperCase(),
                          style: const TextStyle(
                            fontSize: 8,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            
            // Content
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      region['name'].toString(),
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    
                    // Row values
                    Column(
                      children: [
                        _buildStatRow(Icons.groups_rounded, 'Pop.', region['pop'].toString(), AppTheme.primary),
                        const SizedBox(height: 4),
                        _buildStatRow(Icons.school_rounded, 'Scol.', region['scol'].toString(), AppTheme.secondary),
                      ],
                    ),
                    
                    // CTA Button
                    SizedBox(
                      width: double.infinity,
                      height: 24,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primary.withOpacity(0.1),
                          foregroundColor: AppTheme.primary,
                          padding: EdgeInsets.zero,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        onPressed: () {
                          widget.onQuestionSelected(
                            "Donne-moi les détails statistiques de la région de ${region['name']}"
                          );
                        },
                        child: const Text(
                          'Interroger l\'IA',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(IconData icon, String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Icon(icon, size: 12, color: AppTheme.textTertiary),
            const SizedBox(width: 4),
            Text(
              label,
              style: const TextStyle(fontSize: 10, color: AppTheme.textSecondary),
            ),
          ],
        ),
        Text(
          value,
          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: color == AppTheme.secondary ? AppTheme.textPrimary : color),
        ),
      ],
    );
  }
}
