# syntax = docker/dockerfile:1

ARG RUBY_VERSION=3.4.7
FROM docker.io/library/ruby:$RUBY_VERSION-slim AS base

WORKDIR /rails

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
      build-essential git pkg-config libyaml-dev \
      curl libjemalloc2 libvips sqlite3 libsqlite3-dev && \
    rm -rf /var/lib/apt/lists /var/cache/apt/archives

RUN gem install bundler -v 2.7.2

ENV BUNDLE_PATH=/bundle \
    BUNDLE_WITHOUT="" \
    BUNDLE_WITH="development test" \
    RAILS_ENV=production

COPY Gemfile Gemfile.lock ./
RUN bundle config set --local path "$BUNDLE_PATH" && \
    bundle config set --local without "$BUNDLE_WITHOUT" && \
    bundle install && \
    rm -rf ~/.bundle "$BUNDLE_PATH"/ruby/*/cache "$BUNDLE_PATH"/ruby/*/bundler/gems/*/.git

COPY . .

RUN SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

EXPOSE 3000
CMD ["./bin/rails", "server", "-b", "0.0.0.0", "-p", "3000"]
