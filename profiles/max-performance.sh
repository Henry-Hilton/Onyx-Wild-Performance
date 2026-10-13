#!/system/bin/sh
# Optional live profile: supported maximum clocks and minimum latency.
# Run with root after boot: sh /path/to/max-performance.sh
# Reboot restores the ROM defaults. Kernel thermal controls remain active.
set -u
set_value() {
  path=$1
  value=$2
  if [ -w "$path" ]; then
    printf '%s\n' "$value" > "$path" 2>/dev/null && echo "$path=$value"
  fi
}
for policy in /sys/devices/system/cpu/cpufreq/policy*; do
  [ -d "$policy" ] || continue
  if grep -qw performance "$policy/scaling_available_governors"; then
    set_value "$policy/scaling_governor" performance
  fi
  for governor in "$policy/schedutil" "$policy/walt"; do
    set_value "$governor/up_rate_limit_us" 0
    set_value "$governor/down_rate_limit_us" 20000
    set_value "$governor/hispeed_load" 80
  done
done
gpu=/sys/class/kgsl/kgsl-3d0
if [ -r "$gpu/devfreq/available_governors" ] && grep -qw performance "$gpu/devfreq/available_governors"; then
  set_value "$gpu/devfreq/governor" performance
fi
for setting in force_clk_on force_bus_on force_rail_on force_no_nap; do
  set_value "$gpu/$setting" 1
done
set_value /proc/sys/net/core/default_qdisc fq
set_value /proc/sys/net/ipv4/tcp_congestion_control bbr3
set_value /proc/sys/vm/vfs_cache_pressure 50
echo 'Maximum performance profile applied. Reboot to restore ROM defaults.'
