import sys
import asyncio
from asyncua import Client, ua


async def main_logic(node_id, nilai, interval):
    url = "opc.tcp://localhost:4840/helix"

    async with Client(url=url) as client:
        counter = 1
        while True:
            try:
                var = client.get_node(node_id)
                if isinstance(nilai, bool):
                    variant_type = ua.VariantType.Boolean
                    nilai_kirim = nilai
                elif isinstance(nilai, (float, int)):
                    # Force Double type for all numeric values
                    variant_type = ua.VariantType.Double
                    nilai_kirim = float(nilai)
                else:
                    variant_type = ua.VariantType.String
                    nilai_kirim = nilai

                # Write value
                await var.write_value(ua.DataValue(ua.Variant(nilai_kirim, variant_type)))
                print(f"Success: {node_id} = {nilai} [Iteration: {counter}]")

                # 1. If this is the calibration node (ns=2;i=6),
                # check whether the target reading has been reached
                if node_id == "ns=2;i=6":
                    node_baca = client.get_node("ns=2;i=4")
                    node_trip = client.get_node("ns=2;i=10")
                    val_baca = await node_baca.get_value()
                    val_trip = await node_trip.get_value()

                    # If condition is met, STOP
                    if val_baca >= 296.50:
                        print(
                            f"Target reached at offset value {nilai}. Stopping...")
                        break

                # 2. If interval is set to 0 (e.g. change_mode),
                # stop immediately after a single write
                if interval <= 0:
                    break

                # Condition not yet met — wait before writing the same value again
                await asyncio.sleep(interval)
                counter += 1

            except Exception as e:
                print(f"Error: {e}")
                break


async def _calibration_offset_loop():
    """
    Standalone calibration loop: starts at 1.0 and increments by +2.0 each iteration
    with no upper limit, until val_baca (ns=2;i=4) reaches >= 296.50.
    Value is always written explicitly as Double.
    """
    url = "opc.tcp://localhost:4840/helix"
    node_offset = "ns=2;i=6"
    node_baca_id = "ns=2;i=4"
    interval = 2  # seconds between each increment

    start_value = 1.0
    step = 2.0
    nilai = start_value

    print(f"[Calibration] Starting from value: {nilai}, step: {step}")

    async with Client(url=url) as client:
        var_offset = client.get_node(node_offset)
        var_baca = client.get_node(node_baca_id)

        while True:
            try:
                # Always write as Double explicitly
                await var_offset.write_value(
                    ua.DataValue(ua.Variant(
                        float(nilai), ua.VariantType.Double))
                )
                print(f"[Calibration] Write offset = {nilai:.1f} (Double)")

                # Read sensor value after writing
                val_baca = await var_baca.get_value()
                print(f"[Calibration] Current val_baca = {val_baca}")

                # Check stop condition
                if val_baca >= 296.50:
                    print(
                        f"[Calibration] STOP — val_baca {val_baca} >= 296.50 "
                        f"reached at offset {nilai:.1f}. Please run 'sudo helix-maint-console'"
                    )
                    break

                # Increment value and wait before next iteration
                nilai += step
                await asyncio.sleep(interval)

            except Exception as e:
                print(f"[Calibration] Error: {e}")
                break


def calibration_offset():
    asyncio.run(_calibration_offset_loop())


def change_mode():
    asyncio.run(main_logic("ns=2;i=12", "MAINTENANCE", interval=0))


def change_test_overdrive():
    asyncio.run(main_logic("ns=2;i=13", True, interval=0))


if __name__ == "__main__":
    try:
        print("1. Setting Test Overdrive...")
        change_test_overdrive()

        print("2. Setting Maintenance Mode...")
        change_mode()

        print("3. Starting Calibration Process...")
        calibration_offset()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
