FROM ubuntu:latest

RUN apt-get update && apt-get -y install cron

# Copy runner file to the cron.d directory
COPY runner /etc/cron.d/runner

# Give read permissions to the cron job
RUN chmod 0644 /etc/cron.d/runner

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the cron service
CMD ["cron", "-f"]

