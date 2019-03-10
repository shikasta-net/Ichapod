#!/bin/bash
# Ichapod by Patrick Simonds (divinitycycle@gmail.com)
# This script is inspired by BashPodder, but I wanted much fancier output options

##############
## SETTINGS ##
##############
# Move the settings to a global locaiton
. /etc/default/ichapod

####################################
# Funcitons to simplify the script #
####################################
function log_info {
	echo "$(date +\%m-\%d-\%I:\%M\%p): $1">>"$debuglog"
	if [ -s "$dailylog" ]
	then
		echo "$1">>"$dailylog";
	fi
}

# Begin actual script #############################
# First we check that the daily log variables havbe been set, but the current log file is empty.
# If so, its the first run of the day, and we should output the header.
if [ ! -s "$dailylog" ] && [ "$dailylogheader" != "" ] && [ "$dailylog" != "" ]
then
	mkdir -p "$(dirname $dailylog)"
	echo "$dailylogheader">>"$dailylog";
fi
log_info "Ichapod started.";
# Wrap up the functional stuff using flock to prevent concurrent runs.
set -e

(
	flock -x -w 10 200
	# Next we make sure our destination actually exists
	mkdir -p $destinationfolder;
	# if download log doesn't exist, make one.
	if [ ! -e "$downloadlog" ];
	then
		log_info "Download Log missing, should be $downloadlog.";
		touch "$downloadlog";
	fi
	if [ -e "$downloadlog" ];
	then
		log_info "Download Log found at $downloadlog.";
	fi
	# Ensure no previous temp log file exists
	rm -f /tmp/ichapodtmp.log;
	# Now we read through the podcast list and handle each one
	while read podcast
	do
		if [[ ${podcast:0:1} != "#" ]];
		then
			# Avoiding some logic issues by freshly instantiated variables at the start of each podcast
			label="";
			label2="";
			ageskip="";
			ageseconds="";
			# check to see if a custom label has been entered for this feed
			if [[ "$podcast" = *---* ]];
			then
				piece1=${podcast%---*}; # Break the podcast text into two chunks to check for labels
				piece2=${podcast#*---};
				# Do some tricky string processing to figure out where the download URL is
				if [[ "${piece2:0:8}" =~ ^https?:// ]];
				then
					label="$piece1";
					feedurl="$piece2";
				else
					label=${piece1%---*};
					feedurl=${piece2#*---};
					label2=${piece2%---*};
				fi
			else
				feedurl=$podcast;
			fi #now we pull & process the feed items from the current podcast feed we are processing.
			log_info "Now working on $label-$label2-$feedurl.";
			wget -O - -o $debuglog $feedurl | xsltproc $processorfile - > /tmp/ichapodtmp.log;
			# Episodes are downloaded in reverse order so number in reverse from the most recent
			episodenumber="$(wc -l < /tmp/ichapodtmp.log)";
			while read episode
			do
				# This is the loop that processes each episode within a podcast.
				if [ "$label" != "" ];
				then
					episode=${episode#*---}; # we don't need the label from the feed so chop off the first chunk
				fi
				if [ "$label" == "" ];
				then
					label=${episode%---*}; # Since we didn't get a label from the podcast list, we just use the one from the feed
					label=${label%---*};
					label=${label%---*};
					label=${label%---*};
					episode=${episode#*---};
				fi
				date=${episode%---*}; # Next pull in the date for the episode
				date=${date%---*};
				date=${date%---*};
				episode=${episode#*---};
				ageseconds=$(date -d "$date" +%s);
				year=$(date -d "$date" +%Y);
				date=$(date -d "$date" +%Y-%m-%d-%H%M); # put the date into the nice 2011-12-03 format
				episodetitle=${episode%---*}; # Next the title
				episodetitle=${episodetitle%---*}; # Next the title
				episodetitle=$(echo ${episodetitle//—/-}); # Replace unicode emdash with "-" in the title.
				episodetitle=$(echo ${episodetitle//’/\'}); # Replace unicode tic with "'" in the title.
				episode=${episode#*---};
				# the filetype and extsion
				filetype=${episode#*---};
				case "$filetype" in
						audio/mp4 | audio/x-m4a)
								fileext=m4a
								;;
						audio/mpeg)
								fileext=mp3
								;;
						*)
								log_info "Unknown filetype $filetype. Fallback to mp3."
								fileext=mp3
								;;
				esac
				# the actual wget target
				downloadurl=${episode%---*};
				# Now that all the episode-specific variables SHOULD be filled, we can read them out to the debug log.
				log_info "Now working on $downloadurl.";
				log_info "Episode Title is $episodetitle.";
				log_info "Date is $date, Year is $year.";
				# Here's the date processing section. I decided that rather than wrap everything inside another logic fork, I'd just do the date comparison
				# and then fill a Boolean variable with the result. Instantiate that with "false" to avoid any logic problems.
				ageskip=false;
				# On the left side of "greater than" we have the current date in GNU seconds format, minus the episode date in the same format.
				# AKA "how old it is"
				# on the right we simply multiply the age limit by 86,400 (the number of seconds in a day) so that its the same format.
				if [ $agelimit -gt 0 ] && [ $(($( date +%s)-$ageseconds)) -gt $(($agelimit*86400)) ]
				then
					ageskip=true;
					log_info "Skipping $label-$date-$episodetitle.$fileext, too old.";
				fi
				# If the file isn't already in the log and isn't too old, then lets go!
				if ! grep "$downloadurl" "$downloadlog">/dev/null && ! $ageskip
				then
					fileepisodetitle=$episodetitle;
					fileepisodetitle=$(echo ${fileepisodetitle// - /, }); # Replace " - " with ", " to avoid confusion in name convention.
					fileepisodetitle=$(echo ${fileepisodetitle//\?/}); # Remove question marks.
					fileepisodetitle=$(echo ${fileepisodetitle//:/, }); # Replace ":" with ", ".
					fileepisodetitle=$(echo ${fileepisodetitle// \/ /, }); # Replace " / " with ", ".
					fileepisodetitle=$(echo ${fileepisodetitle//\//, }); # Replace "/" with ",".
					fileepisodetitle=$(echo ${fileepisodetitle//\//}); # Remove any remaining "/"s.
					fileepisodetitle=$(echo "$fileepisodetitle" | tr -s " ") # Collapse multiple spaces
					fileepisodetitle=$(echo ${fileepisodetitle// ,/,}) # Remove space preceeding a comma
					if [ "$label2" == "" ];
					then  # There are some variables that are different if you have only one "label" to work with.
						mkdir -p "$destinationfolder/$label"; # Need to make sure the destination folder is there or wget won't work
						album="$label";
						finishedfilename="$destinationfolder/$label/$date - $fileepisodetitle - $label.$fileext";
						coverartlocation="$destinationfolder/$label/Folder.jpg";
					fi
					if [ "$label2" != "" ]; # Here's the other version, for if you have 2 labels.
					then
						mkdir -p "$destinationfolder/$label/$label2";
						album="$label2";
						finishedfilename="$destinationfolder/$label/$label2/$date - $fileepisodetitle - $label - $label2.$fileext";
						coverartlocation="$destinationfolder/$label/$label2/Folder.jpg";
					fi
					# If file DOES exist already, that seems weird.
					if [ -e "$finishedfilename" ]
					then
						log_info "URL not found in log, but $finishedfilename but file exists anyway.";
					fi
					# only download if file doesn't already exist
					if [ ! -e "$finishedfilename" ]
					then
						log_info "Downloading $finishedfilename.";
						wget -q -x -t 10 -O "$finishedfilename" "$downloadurl"; # Download the file.
						if [ -e "$finishedfilename" ] && [ "$fileext" == "mp3" ] # If the downloaded file exists, then we can proceed to deal with it.
						then
							echo "$downloadurl" >> "$downloadlog"; # Log it, and tag it.
							log_info "Now running eyeD3.";
							eyeD3 --no-color --to-v2.3 --set-text-frame=TPE2:"$label" --genre=Podcast --year=$year --title="$episodetitle" --album="$album" --artist="$label" --track="$episodenumber" "$finishedfilename">>"$debuglog" 2>&1;
							log_info "eyeD3 done."
							if [ -e "$coverartlocation" ] # Check for cover art file, and if it exists, tag it into the file.
							then
								log_info "Now tagging the artwork in.";
								eyeD3 --no-color --remove-images "$finishedfilename">>"$debuglog";
								eyeD3 --no-color --to-v2.3 --add-image="$coverartlocation":FRONT_COVER "$finishedfilename">>"$debuglog";
								log_info "eyeD3 done."
							fi
							# Check the mp3 to see if it has already been run through ReplayGain and skip it if it has.
							if ! eyeD3 "$finishedfilename" | grep replaygain_reference_loudness>/dev/null;
							then
								log_info "Applying ReplayGain to file.";
								replaygain -f --no-album "$finishedfilename">>"$debuglog" 2>&1; # Normalize the file
								log_info "ReplayGain done."
							fi
							log_info "End post-processing.";
						fi # END Post-Processing Branch.
					fi # END Downloader
				fi # END Downloader Branch.
				episodenumber=$((episodenumber - 1)); # Decrement the episode counter
			done < "/tmp/ichapodtmp.log"
			log_info "Finished with this feed.";
		fi
	done < "$podcastlist"
	log_info "Removing temporary log, processing complete.";
	rm -f /tmp/ichapodtmp.log;
) 200>/var/lock/.inchapod.exclusivelock
