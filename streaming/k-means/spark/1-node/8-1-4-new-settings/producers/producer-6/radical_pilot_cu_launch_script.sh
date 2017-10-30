#!/bin/sh


# Environment variables
export RP_SESSION_ID="rp.session.one.george.017466.0003"
export RP_PILOT_ID="pilot.0000"
export RP_AGENT_ID="agent_0"
export RP_SPAWNER_ID="agent.executing.0.child"
export RP_UNIT_ID="unit.000005"
export RP_GTOD="/work/03662/tg829618/wrangler/radical.pilot.sandbox/rp.session.one.george.017466.0003/pilot.0000/gtod"
export RP_PROF="/work/03662/tg829618/wrangler/radical.pilot.sandbox/rp.session.one.george.017466.0003/pilot.0000/unit.000005/PROF"
export RP_TMP="None"


touch $RP_PROF

# Change to unit sandbox
cd /work/03662/tg829618/wrangler/radical.pilot.sandbox/rp.session.one.george.017466.0003/pilot.0000/unit.000005

# The command to run
python "data_producer.py" "c251-123:9092" 
RETVAL=$?

# Exit the script with the return code from the command
exit $RETVAL
