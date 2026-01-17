import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';

/// Score Gauge Widget - Tachometer Display
class ScoreGauge extends StatelessWidget {
  final double score;
  final double maxScore;
  final String label;

  const ScoreGauge({
    super.key,
    required this.score,
    this.maxScore = 10.0,
    this.label = 'Gesamtscore',
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 250,
          child: SfRadialGauge(
            axes: <RadialAxis>[
              RadialAxis(
                minimum: 0,
                maximum: maxScore,
                startAngle: 180,
                endAngle: 0,
                showLabels: true,
                showTicks: true,
                canScaleToFit: true,
                interval: 1,
                minorTicksPerInterval: 0,
                axisLineStyle: const AxisLineStyle(
                  thickness: 0.15,
                  thicknessUnit: GaugeSizeUnit.factor,
                ),
                pointers: <GaugePointer>[
                  NeedlePointer(
                    value: score,
                    needleLength: 0.7,
                    needleStartWidth: 1,
                    needleEndWidth: 5,
                    needleColor: _getScoreColor(score),
                    knobStyle: KnobStyle(
                      knobRadius: 0.08,
                      sizeUnit: GaugeSizeUnit.factor,
                      color: Colors.white,
                      borderColor: _getScoreColor(score),
                      borderWidth: 0.02,
                    ),
                  ),
                ],
                ranges: <GaugeRange>[
                  // Green (Low Risk)
                  GaugeRange(
                    startValue: 0,
                    endValue: 3,
                    color: Colors.green,
                    startWidth: 0.15,
                    endWidth: 0.15,
                    sizeUnit: GaugeSizeUnit.factor,
                  ),
                  // Orange (Medium)
                  GaugeRange(
                    startValue: 3,
                    endValue: 6,
                    color: Colors.orange,
                    startWidth: 0.15,
                    endWidth: 0.15,
                    sizeUnit: GaugeSizeUnit.factor,
                  ),
                  // Red (High Risk)
                  GaugeRange(
                    startValue: 6,
                    endValue: maxScore,
                    color: Colors.red,
                    startWidth: 0.15,
                    endWidth: 0.15,
                    sizeUnit: GaugeSizeUnit.factor,
                  ),
                ],
                annotations: <GaugeAnnotation>[
                  GaugeAnnotation(
                    widget: Container(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            score.toStringAsFixed(1),
                            style: Theme.of(context).textTheme.displayMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: _getScoreColor(score),
                                ),
                          ),
                          Text(
                            _getScoreLabel(score),
                            style: Theme.of(context).textTheme.bodyMedium,
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                    angle: 90,
                    positionFactor: 0.8,
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Color _getScoreColor(double score) {
    if (score < 3) return Colors.green;
    if (score < 6) return Colors.orange;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score < 3) return 'Niedrig\nWenig Risiko';
    if (score < 6) return 'Mittel\nEinige Bedenken';
    if (score < 8) return 'Hoch\nViele Warnsignale';
    return 'Sehr Hoch\nKritisch';
  }
}
