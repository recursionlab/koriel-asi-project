# src/extreme_stress.py
import time

import numpy as np

from dec import d2_norm
from model import TinyByteLM


class ExtremeStressTester:
    """Push system to absolute breaking point and beyond"""

    def __init__(self):
        self.breaking_points = []

    def test_memory_bomb(self):
        """Find exact memory limits"""
        print("=== MEMORY BOMB TEST ===")

        # Progressive memory pressure
        dimensions = [64, 128, 256, 512, 1024, 2048]

        for d in dimensions:
            try:
                print(f"Testing dimension {d}...")
                model = TinyByteLM(ctx=256, d=d, seed=42)
                x = np.random.randint(0, 256, (8, 256), dtype=np.uint8)
                y = np.random.randint(0, 256, (8, 256), dtype=np.uint8)

                start_time = time.time()
                loss, probs, h1 = model.step(x, y, lr=0.1)
                step_time = time.time() - start_time

                memory_mb = (
                    model.E.nbytes
                    + model.W1.nbytes
                    + model.W2.nbytes
                    + x.nbytes
                    + y.nbytes
                ) / 1e6

                print(f"  SUCCESS: {step_time:.3f}s, {memory_mb:.1f}MB")

                if step_time > 5.0:  # Performance cliff
                    self.breaking_points.append(("performance_cliff", d, step_time))
                    print(f"  PERFORMANCE CLIFF at dimension {d}")
                    break

            except MemoryError:
                self.breaking_points.append(("memory_limit", d, "OOM"))
                print(f"  MEMORY LIMIT: {d}")
                break
            except Exception as e:
                self.breaking_points.append(("unexpected_error", d, str(e)))
                print(f"  UNEXPECTED ERROR: {str(e)}")
                break

    def test_sequence_explosion(self):
        """Test extremely long sequences"""
        print("\\n=== SEQUENCE LENGTH EXPLOSION ===")

        # Exponential sequence growth
        lengths = [512, 1024, 2048, 4096, 8192, 16384]

        for seq_len in lengths:
            try:
                print(f"Testing sequence length {seq_len}...")
                model = TinyByteLM(ctx=seq_len, d=32, seed=42)

                # Create sequence in chunks to avoid creation failure
                chunk_size = 1024
                x_chunks = []
                y_chunks = []

                for i in range(0, seq_len, chunk_size):
                    end = min(i + chunk_size, seq_len)
                    x_chunks.append(
                        np.random.randint(0, 256, (end - i,), dtype=np.uint8)
                    )
                    y_chunks.append(
                        np.random.randint(0, 256, (end - i,), dtype=np.uint8)
                    )

                x = np.concatenate(x_chunks).reshape(1, -1)
                y = np.concatenate(y_chunks).reshape(1, -1)

                start_time = time.time()
                loss, probs, h1 = model.step(x, y, lr=0.1)
                step_time = time.time() - start_time

                memory_usage = (x.nbytes + y.nbytes + model.E.nbytes) / 1e6
                print(f"  SUCCESS: {step_time:.3f}s, {memory_usage:.1f}MB")

                if step_time > 10.0:
                    self.breaking_points.append(
                        ("sequence_time_limit", seq_len, step_time)
                    )
                    print(f"  TIME LIMIT at sequence {seq_len}")
                    break

            except MemoryError:
                self.breaking_points.append(("sequence_memory_limit", seq_len, "OOM"))
                print(f"  MEMORY LIMIT: {seq_len}")
                break
            except Exception as e:
                self.breaking_points.append(("sequence_error", seq_len, str(e)))
                print(f"  ERROR: {str(e)}")
                break

    def test_numerical_chaos(self):
        """Test system with chaotic numerical inputs"""
        print("\\n=== NUMERICAL CHAOS TEST ===")

        chaos_tests = [
            ("inf_values", lambda: np.array([np.inf, -np.inf, 1.0, 0.0])),
            ("nan_values", lambda: np.array([np.nan, np.nan, 1.0, 0.0])),
            ("huge_values", lambda: np.array([1e100, -1e100, 1e50, -1e50])),
            ("tiny_values", lambda: np.array([1e-100, 1e-200, 1e-300, 1e-400])),
            ("mixed_chaos", lambda: np.array([np.inf, 1e-300, np.nan, 1e100])),
        ]

        for test_name, value_gen in chaos_tests:
            try:
                print(f"Testing {test_name}...")
                omega = value_gen()

                # Test DEC operations
                d2_result = d2_norm(omega)

                if not np.isfinite(d2_result):
                    self.breaking_points.append(
                        ("numerical_instability", test_name, d2_result)
                    )
                    print(f"  NUMERICAL INSTABILITY: {d2_result}")
                else:
                    print(f"  SURVIVED: {d2_result}")

            except Exception as e:
                self.breaking_points.append(("numerical_error", test_name, str(e)))
                print(f"  ERROR: {str(e)}")

    def test_adversarial_inputs(self):
        """Test with adversarially crafted inputs"""
        print("\\n=== ADVERSARIAL INPUT TEST ===")

        adversarial_tests = [
            ("all_zeros", lambda size: np.zeros(size, dtype=np.uint8)),
            ("all_max", lambda size: np.full(size, 255, dtype=np.uint8)),
            (
                "alternating",
                lambda size: np.array(
                    [i % 2 * 255 for i in range(size)], dtype=np.uint8
                ),
            ),
            (
                "sawtooth",
                lambda size: np.array([i % 256 for i in range(size)], dtype=np.uint8),
            ),
            (
                "random_extremes",
                lambda size: np.random.choice([0, 255], size).astype(np.uint8),
            ),
        ]

        for test_name, input_gen in adversarial_tests:
            try:
                print(f"Testing {test_name}...")
                model = TinyByteLM(ctx=128, d=32, seed=42)

                x = input_gen((4, 128))
                y = input_gen((4, 128))

                losses = []
                for step in range(10):  # Multiple steps to see pattern
                    loss, probs, h1 = model.step(x, y, lr=0.1)
                    losses.append(loss)

                # Check for pathological behavior
                loss_std = np.std(losses)
                loss_mean = np.mean(losses)

                if loss_std < 1e-6:  # No learning
                    self.breaking_points.append(
                        ("no_learning", test_name, f"loss_std={loss_std}")
                    )
                    print(f"  NO LEARNING: std={loss_std:.8f}")
                elif loss_mean > 20.0:  # Exploding loss
                    self.breaking_points.append(
                        ("exploding_loss", test_name, f"mean_loss={loss_mean}")
                    )
                    print(f"  EXPLODING LOSS: {loss_mean:.3f}")
                else:
                    print(f"  SURVIVED: mean={loss_mean:.3f}, std={loss_std:.6f}")

            except Exception as e:
                self.breaking_points.append(("adversarial_error", test_name, str(e)))
                print(f"  ERROR: {str(e)}")

    def test_concurrent_stress(self):
        """Test multiple models running simultaneously"""
        print("\\n=== CONCURRENT STRESS TEST ===")

        try:
            models = []
            print("Creating multiple models...")

            # Create many models simultaneously
            for i in range(20):
                model = TinyByteLM(ctx=64, d=16, seed=i)
                models.append(model)
                print(f"  Model {i+1}/20 created")

            print("Running concurrent training steps...")
            start_time = time.time()

            for i, model in enumerate(models):
                x = np.random.randint(0, 256, (2, 64), dtype=np.uint8)
                y = np.random.randint(0, 256, (2, 64), dtype=np.uint8)
                loss, probs, h1 = model.step(x, y, lr=0.1)

            total_time = time.time() - start_time
            print(f"  CONCURRENT SUCCESS: {total_time:.3f}s for {len(models)} models")

        except Exception as e:
            self.breaking_points.append(("concurrent_error", len(models), str(e)))
            print(f"  CONCURRENT ERROR: {str(e)}")

    def run_extreme_tests(self):
        """Execute all extreme stress tests"""
        print("STARTING EXTREME STRESS TEST BATTERY")
        print("Goal: Find breaking points and failure modes")

        try:
            self.test_memory_bomb()
        except Exception as e:
            print(f"Memory bomb test crashed: {e}")

        try:
            self.test_sequence_explosion()
        except Exception as e:
            print(f"Sequence explosion test crashed: {e}")

        try:
            self.test_numerical_chaos()
        except Exception as e:
            print(f"Numerical chaos test crashed: {e}")

        try:
            self.test_adversarial_inputs()
        except Exception as e:
            print(f"Adversarial input test crashed: {e}")

        try:
            self.test_concurrent_stress()
        except Exception as e:
            print(f"Concurrent stress test crashed: {e}")

        print("\\nEXTREME STRESS TEST COMPLETE")
        print(f"Breaking points found: {len(self.breaking_points)}")

        for bp_type, detail, info in self.breaking_points:
            print(f"  {bp_type}: {detail} -> {info}")

        return self.breaking_points


def main():
    tester = ExtremeStressTester()
    breaking_points = tester.run_extreme_tests()

    print("\\nSYSTEM ANALYSIS:")
    if len(breaking_points) == 0:
        print("EXTREMELY ROBUST - No breaking points found!")
        print("RECOMMENDATION: Increase challenge level further")
    else:
        print(f"Found {len(breaking_points)} breaking points")
        print("STRUCTURAL ADAPTATIONS NEEDED:")

        for bp_type, detail, info in breaking_points:
            if "memory" in bp_type:
                print("  -> Implement memory streaming and gradient checkpointing")
            elif "time" in bp_type:
                print("  -> Add computational optimization and caching")
            elif "numerical" in bp_type:
                print("  -> Add numerical stability safeguards")
            elif "learning" in bp_type:
                print("  -> Implement adaptive learning rate and regularization")

    return breaking_points


if __name__ == "__main__":
    main()
