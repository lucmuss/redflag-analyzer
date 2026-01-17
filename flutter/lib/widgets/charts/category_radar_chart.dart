import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../models/analysis.dart';

/// Category Radar Chart Widget
class CategoryRadarChart extends StatelessWidget {
  final CategoryScores categoryScores;
  final double maxValue;

  const CategoryRadarChart({
    super.key,
    required this.categoryScores,
    this.maxValue = 10.0,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          'Kategorie-Analyse',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 24),
        AspectRatio(
          aspectRatio: 1.3,
          child: RadarChart(
            RadarChartData(
              radarShape: RadarShape.polygon,
              tickCount: 5,
              ticksTextStyle: Theme.of(context).textTheme.bodySmall!,
              tickBorderData: const BorderSide(color: Colors.transparent),
              gridBorderData: BorderSide(
                color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
                width: 1,
              ),
              radarBorderData: BorderSide(
                color: Theme.of(context).colorScheme.outline,
                width: 2,
              ),
              titlePositionPercentageOffset: 0.15,
              titleTextStyle: Theme.of(context).textTheme.titleSmall!.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              getTitle: (index, angle) {
                switch (index) {
                  case 0:
                    return RadarChartTitle(
                      text: 'Vertrauen',
                      angle: angle,
                    );
                  case 1:
                    return RadarChartTitle(
                      text: 'Verhalten',
                      angle: angle,
                    );
                  case 2:
                    return RadarChartTitle(
                      text: 'Werte',
                      angle: angle,
                    );
                  case 3:
                    return RadarChartTitle(
                      text: 'Dynamik',
                      angle: angle,
                    );
                  default:
                    return const RadarChartTitle(text: '');
                }
              },
              dataSets: [
                RadarDataSet(
                  fillColor: Theme.of(context)
                      .colorScheme
                      .primary
                      .withOpacity(0.2),
                  borderColor: Theme.of(context).colorScheme.primary,
                  borderWidth: 2,
                  entryRadius: 3,
                  dataEntries: [
                    RadarEntry(value: categoryScores.trust),
                    RadarEntry(value: categoryScores.behavior),
                    RadarEntry(value: categoryScores.values),
                    RadarEntry(value: categoryScores.dynamics),
                  ],
                ),
              ],
              radarBackgroundColor: Colors.transparent,
              radarTouchData: RadarTouchData(
                enabled: true,
                touchCallback: (FlTouchEvent event, response) {},
              ),
            ),
          ),
        ),
        const SizedBox(height: 24),
        _buildLegend(context),
      ],
    );
  }

  Widget _buildLegend(BuildContext context) {
    return Wrap(
      spacing: 16,
      runSpacing: 12,
      alignment: WrapAlignment.center,
      children: [
        _buildLegendItem(
          context,
          'Vertrauen',
          categoryScores.trust,
          Colors.blue,
        ),
        _buildLegendItem(
          context,
          'Verhalten',
          categoryScores.behavior,
          Colors.green,
        ),
        _buildLegendItem(
          context,
          'Werte',
          categoryScores.values,
          Colors.orange,
        ),
        _buildLegendItem(
          context,
          'Dynamik',
          categoryScores.dynamics,
          Colors.purple,
        ),
      ],
    );
  }

  Widget _buildLegendItem(
    BuildContext context,
    String label,
    double value,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(width: 8),
          Text(
            value.toStringAsFixed(1),
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
          ),
        ],
      ),
    );
  }
}
