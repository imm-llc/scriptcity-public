%define name tls_monitor
%define version 1.1
%define unmangled_version 1.0
%define unmangled_version 1.0
%define release 1
%define _tmppath /tmp/rpm


Summary: TLS Expiration Monitor
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}.tar.gz
Requires: python36 python36-setuptools
License: None
Group: Monitoring
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Mitch Anderson <manderson@boulderheavyindustries.com>
Url: https://github.com/imm-llc/scriptcity-public/tree/master/cert-expiry-check

%description



%prep
rm -rf %{_tmppath}/*
rm -rf %{_builddir}/*
rm -rf %{buildroot}/*


%setup -c -n %{name}

%build

%install
mkdir -p %{buildroot}/usr/local/bin/tls_monitor
mkdir -p %{buildroot}/etc/tls_monitor
mkdir -p %{buildroot}/etc/cron.d
mkdir -p %{buildroot}/var/log/tls_monitor


install -m 0640 %{_builddir}/%{name}/check_v2.py %{buildroot}/usr/local/bin/tls_monitor/
install -m 0640 %{_builddir}/%{name}/slack_alert.py %{buildroot}/usr/local/bin/tls_monitor/
install -m 0640 %{_builddir}/%{name}/config.cfg %{buildroot}/etc/tls_monitor
install -m 0640 %{_builddir}/%{name}/pipfile %{buildroot}/usr/local/bin/tls_monitor/pipfile
install -m 0640 %{_builddir}/%{name}/tls_monitor_cron %{buildroot}/etc/cron.d/
touch %{buildroot}/var/log/tls_monitor/app.log

%pre

if [ "$1" = "1" ]; then
    echo "##############################"
    echo "Installing TLS Monitor"
    if [ ! $(id -u tls_monitor 2> /dev/null) ] 
    then 
    echo "##############################"
    echo "Could not find tls_monitor user....creating"
    adduser --system --no-create-home --shell /sbin/nologin tls_monitor
    echo "##############################"
    echo "User created"
    fi
fi

if [ "$1" = "2" ]; then
  echo "##############################"
  echo "Backing up previous installation to /usr/local/bin/tls_monitor-$(date +%F)"
  #mv /usr/local/bin/bin/tls_monitor /usr/local/bin/bin/tls_monitor-$(date +%F)
fi

%post 

if [ "$1" = "1" ]; then
    echo "##############################"
    echo "Checking dependencies"
    if [ ! -f /usr/local/bin/pip3 ]
        then
        echo "pip3 not installed.....installing"
        /usr/bin/easy_install-3.6 pip 1> /dev/null
    fi
    echo "##############################"
    echo "Installing python dependencies"
    /usr/local/bin/pip3 install -r /usr/local/bin/tls_monitor/pipfile 
fi

if [ "$1" = "2" ]; then
  echo "##############################"
  echo "Upgrading TLS Monitor...performing post installation tasks"
  echo "##############################"
  echo "Ready to use!"
fi


%clean
rm -rf %{_builddir}/*
rm -rf %{buildroot}/*

%files
%defattr(-,tls_monitor,root)
/usr/local/bin/tls_monitor/
%attr(0644,root,root) /etc/cron.d/tls_monitor_cron
%attr(0755,tls_monitor,tls_monitor) /var/log/tls_monitor
%attr(0644,tls_monitor,tls_monitor) /var/log/tls_monitor/app.log
%config %attr(0644,tls_monitor,tls_monitor) /etc/tls_monitor/config.cfg