# configure options
#
# Some can be overriden on rpmbuild commandline with:
# rpmbuild --define 'variable value'
#   (use any value, ie 1 for flag "with_XXXX" definitions)
#
# E.g. rpmbuild --define 'release_rev 02' may be useful if building
# rpms again and again on the same day, so the newer rpms can be installed.
# bumping the number each time.

####################### Quagga configure options #########################
# with-feature options
%{!?with_snmp:			%global with_snmp		1 }
%{!?with_vtysh:			%global	with_vtysh		1 }
%{!?with_tcp_zebra:		%global	with_tcp_zebra		0 }
%{!?with_vtysh:			%global	with_vtysh		1 }
%{!?with_pam:			%global	with_pam		1 }
%{!?with_ospfclient:		%global	with_ospfclient		1 }
%{!?with_ospfapi:		%global	with_ospfapi		1 }
%{!?with_irdp:			%global	with_irdp		1 }
%{!?with_rtadv:			%global	with_rtadv		1 }
%{!?with_isisd:			%global	with_isisd		1 }
%{!?with_pimd:			%global	with_pimd		1 }
%{!?with_nhrpd:			%global	with_nhrpd		1 }
%{!?with_shared:		%global	with_shared		1 }
%{!?with_multipath:		%global	with_multipath		64 }
%{!?quagga_user:		%global	quagga_user		quagga }
%{!?vty_group:			%global	vty_group		quaggavt }
%{!?with_fpm:			%global	with_fpm		0 }
%{!?with_watchquagga:		%global	with_watchquagga	1 }
# whether to build doc/quagga.html - requires a lot of TeX packages
%{!?with_texi2html:		%global with_texi2html		0 }

# path defines
%define		_sysconfdir	/etc/quagga
%define		zeb_src		%{_builddir}/%{name}-%{quaggaversion}
%define		zeb_rh_src	%{zeb_src}/redhat
%define		zeb_docs	%{zeb_src}/doc

# defines for configure
%define		_localstatedir	/var/run/quagga
############################################################################

#### Version String tweak
# Remove invalid characters form version string and replace with _
%{expand: %%global rpmversion %(echo '1.2.4' | tr [:blank:]- _ )}
%define		quaggaversion	1.2.4

#### Check version of texi2html 
# Old versions don't support "--number-footnotes" option.
%if %{with_texi2html}
	%{expand: %%global texi2htmlversion %(type texi2html >/dev/null 2>&1 && (rpm -q --qf '%%{VERSION}' texi2html | cut -d. -f1) || echo 0 )}
%endif

#### Check for systemd or init.d (upstart)
# Check for init.d (upstart) as used in CentOS 6 or systemd (ie CentOS 7)
%{expand: %%global initsystem %(if [[ `/sbin/init --version 2> /dev/null` =~ upstart ]]; then echo upstart; elif [[ `systemctl` =~ -\.mount ]]; then echo systemd; fi)}
#
# If init system is systemd, then always disable watchquagga
#
%if "%{initsystem}" == "systemd"
	# Note: For systems with systemd, watchquagga will NOT be built. Systemd
	# takes over the role of restarting crashed processes. Value will
	# be overwritten with 0 below for systemd independent on the setting here
	%global	with_watchquagga 0
%endif

# if FPM is enabled, then enable tcp_zebra as well
#
%if %{with_fpm}
	%global	with_tcp_zebra	1
%endif

# misc internal defines
%{!?quagga_uid:		%global		quagga_uid	92 }
%{!?quagga_gid:		%global		quagga_gid	92 }
%{!?vty_gid:		%global		vty_gid		85 }

%define		daemon_list	zebra ripd ospfd bgpd

%define		daemonv6_list	ripngd ospf6d

%if %{with_isisd}
%define		daemon_isisd	isisd
%else
%define		daemon_isisd	""
%endif

%if %{with_pimd}
%define		daemon_pimd	pimd
%else
%define		daemon_pimd	""
%endif

%if %{with_nhrpd}
%define		daemon_nhrpd	nhrpd
%else
%define		daemon_nhrpd	""
%endif

%if %{with_watchquagga}
%define		daemon_watchquagga	watchquagga
%else
%define		daemon_watchquagga	""
%endif

%define		all_daemons	%{daemon_list} %{daemonv6_list} %{daemon_isisd} %{daemon_pimd} %{daemon_nhrpd} %{daemon_watchquagga}

# allow build dir to be kept
%{!?keep_build:		%global		keep_build	0 }

#release sub-revision (the two digits after the CONFDATE)
%{!?release_rev:	%global		release_rev	01 }

Summary: Routing daemon
Name:			quagga
Version:		%{rpmversion}
Release:		20220301%{release_rev}%{?dist}
License:		GPLv2+
Group:			System Environment/Daemons
Source0:		https://download.savannah.gnu.org/releases/quagga/%{name}-%{quaggaversion}.tar.gz
URL:			https://www.quagga.net
Requires:		ncurses
Requires(pre):	/sbin/install-info
Requires(preun): /sbin/install-info
Requires(post):	/sbin/install-info
BuildRequires:	autoconf patch libcap-devel groff
BuildRequires:	perl-generators pkgconfig
%if %{with_texi2html}
BuildRequires:	texi2html
%endif
%if %{with_snmp}
BuildRequires:	net-snmp-devel
Requires:	net-snmp
%endif
%if %{with_vtysh}
BuildRequires:	readline readline-devel ncurses ncurses-devel
Requires:	ncurses
%endif
%if %{with_pam}
BuildRequires:	pam-devel
Requires:	pam
%endif
%if %{with_nhrpd}
BuildRequires:	c-ares-devel
Requires:	c-ares
%endif
%if "%{initsystem}" == "systemd"
BuildRequires:		systemd
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd
%else
# Initscripts > 5.60 is required for IPv6 support
Requires(pre):		initscripts >= 5.60
%endif
Provides:			routingdaemon = %{version}-%{release}
BuildRoot:			%{_tmppath}/%{name}-%{version}-root
#Obsoletes:			mrt zebra quagga-sysvinit

%define __perl_requires %{zeb_rh_src}/quagga-filter-perl-requires.sh

%description
Quagga is a free software routing protocol suite. 

Quagga supports BGP, OSPFv2, OSPFv3, ISIS, RIP, RIPng, PIM-SSM and NHRP.

%package contrib
Summary: contrib tools for quagga
Group: System Environment/Daemons

%description contrib
Contributed/3rd party tools which may be of use with quagga.

%package devel
Summary: Header and object files for quagga development
Group: System Environment/Daemons
Requires: %{name} = %{version}-%{release}

%description devel
The quagga-devel package contains the header and object files neccessary for
developing OSPF-API and quagga applications.

%prep
%setup -q -n quagga-%{quaggaversion}

%build

%configure \
    --sysconfdir=%{_sysconfdir} \
    --libdir=%{_libdir}/quagga \
    --libexecdir=%{_libexecdir} \
    --localstatedir=%{_localstatedir} \
	--disable-werror \
%if !%{with_shared}
	--disable-shared \
%endif
%if %{with_snmp}
	--enable-snmp \
%endif
%if %{with_multipath}
	--enable-multipath=%{with_multipath} \
%endif
%if %{with_tcp_zebra}
	--enable-tcp-zebra \
%endif
%if %{with_vtysh}
	--enable-vtysh \
%endif
%if %{with_ospfclient}
	--enable-ospfclient=yes \
%else
	--enable-ospfclient=no\
%endif
%if %{with_ospfapi}
	--enable-ospfapi=yes \
%else
	--enable-ospfapi=no \
%endif
%if %{with_irdp}
	--enable-irdp=yes \
%else
	--enable-irdp=no \
%endif
%if %{with_rtadv}
	--enable-rtadv=yes \
%else
	--enable-rtadv=no \
%endif
%if %{with_isisd}
	--enable-isisd \
%else
	--disable-isisd \
%endif
%if %{with_nhrpd}
	--enable-nhrpd \
%else
	--disable-nhrpd \
%endif
%if %{with_pam}
	--with-libpam \
%endif
%if 0%{?quagga_user:1}
	--enable-user=%quagga_user \
	--enable-group=%quagga_user \
%endif
%if 0%{?vty_group:1}
	--enable-vty-group=%vty_group \
%endif
%if %{with_fpm}
	--enable-fpm \
%else
	--disable-fpm \
%endif
%if %{with_watchquagga}
	--enable-watchquagga \
%else
	--disable-watchquagga \
%endif
	--enable-gcc-rdynamic

make %{?_smp_mflags}

%if %{with_texi2html}
	pushd doc
	%if %{texi2htmlversion} < 5
		texi2html --number-sections quagga.texi
	%else
		texi2html --number-footnotes  --number-sections quagga.texi
	%endif
	popd
%endif

%install
mkdir -p %{buildroot}/etc/{quagga,sysconfig,logrotate.d,pam.d} \
	%{buildroot}/var/log/quagga %{buildroot}%{_infodir}
make DESTDIR=%{buildroot} INSTALL="install -p" CP="cp -p" install

# Remove this file, as it is uninstalled and causes errors when building on RH9
rm -rf %{buildroot}/usr/share/info/dir

# install /etc sources
%if "%{initsystem}" == "systemd"
mkdir -p %{buildroot}%{_unitdir}
for daemon in %{all_daemons} ; do
	if [ x"${daemon}" != x"" ] ; then
		install %{zeb_rh_src}/${daemon}.service \
			%{buildroot}%{_unitdir}/${daemon}.service
	fi
done
%else
mkdir -p %{buildroot}/etc/rc.d/init.d
for daemon in %{all_daemons} ; do
	if [ x"${daemon}" != x"" ] ; then
		install %{zeb_rh_src}/${daemon}.init \
			%{buildroot}/etc/rc.d/init.d/${daemon}
	fi
done
%endif

install -m644 %{zeb_rh_src}/quagga.pam \
	%{buildroot}/etc/pam.d/quagga
install -m644 %{zeb_rh_src}/quagga.logrotate \
	%{buildroot}/etc/logrotate.d/quagga
install -m644 %{zeb_rh_src}/quagga.sysconfig \
	%{buildroot}/etc/sysconfig/quagga
install -d -m750  %{buildroot}/var/run/quagga


%if 0%{?_tmpfilesdir:1}
	install -d -m 755 %{buildroot}/%{_tmpfilesdir}
	install -p -m 644 %{zeb_rh_src}/quagga-tmpfs.conf \
		 %{buildroot}/%{_tmpfilesdir}/quagga.conf
%endif

%pre
# add vty_group
%if 0%{?vty_group:1}
if getent group %vty_group > /dev/null ; then : ; else \
	/usr/sbin/groupadd -r -g %vty_gid %vty_group > /dev/null || : ; fi
%endif

# add quagga user and group
%if 0%{?quagga_user:1}
# Ensure that quagga_gid gets correctly allocated
if getent group %quagga_user >/dev/null; then : ; else \
	/usr/sbin/groupadd -g %quagga_gid %quagga_user > /dev/null || : ; \
fi
if getent passwd %quagga_user >/dev/null ; then : ; else \
	/usr/sbin/useradd  -u %quagga_uid -g %quagga_gid -G %vty_group \
		-M -r -s /sbin/nologin -c "Quagga routing suite" \
		-d %_localstatedir %quagga_user 2> /dev/null || : ; \
fi
%endif

%post
# zebra_spec_add_service <service name> <port/proto> <comment>
# e.g. zebra_spec_add_service zebrasrv 2600/tcp "zebra service"

zebra_spec_add_service ()
{
  # Add port /etc/services entry if it isn't already there 
  if [ -f /etc/services ] && \
      ! %__sed -e 's/#.*$//' /etc/services | %__grep -wq $1 ; then
    echo "$1		$2			# $3"  >> /etc/services
  fi
}

zebra_spec_add_service zebrasrv 2600/tcp "zebra service"
zebra_spec_add_service zebra	2601/tcp "zebra vty"
zebra_spec_add_service ripd	2602/tcp "RIPd vty"
zebra_spec_add_service ripngd	2603/tcp "RIPngd vty"
zebra_spec_add_service ospfd	2604/tcp "OSPFd vty"
zebra_spec_add_service bgpd	2605/tcp "BGPd vty"
zebra_spec_add_service ospf6d	2606/tcp "OSPF6d vty"
%if %{with_ospfapi}
zebra_spec_add_service ospfapi	2607/tcp "OSPF-API"
%endif
%if %{with_isisd}
zebra_spec_add_service isisd	2608/tcp "ISISd vty"
%endif
%if %{with_pimd}
zebra_spec_add_service pimd	2611/tcp "PIMd vty"
%endif
%if %{with_nhrpd}
zebra_spec_add_service nhrpd	2612/tcp "NHRPd vty"
%endif

%if "%{initsystem}" == "systemd"
for daemon in %all_daemons ; do
	%systemd_post ${daemon}.service
done
%else
for daemon in %all_daemons ; do
	/sbin/chkconfig --add ${daemon}
done
%endif

if [ -f %{_infodir}/%{name}.inf* ]; then
	/sbin/install-info %{_infodir}/quagga.info %{_infodir}/dir
fi

# Create dummy files if they don't exist so basic functions can be used.
if [ ! -e %{_sysconfdir}/zebra.conf ]; then
	echo "hostname `hostname`" > %{_sysconfdir}/zebra.conf
%if 0%{?quagga_user:1}
	chown %quagga_user:%quagga_user %{_sysconfdir}/zebra.conf*
%endif
	chmod 640 %{_sysconfdir}/zebra.conf
fi
for daemon in %{all_daemons} ; do
	if [ ! -e %{_sysconfdir}/${daemon}.conf ]; then
		touch %{_sysconfdir}/${daemon}.conf
		%if 0%{?quagga_user:1}
			chown %quagga_user:%quagga_user %{_sysconfdir}/${daemon}.conf*
		%endif
	fi
done
%if %{with_watchquagga}
	# No config for watchquagga - this is part of /etc/sysconfig/quagga
	rm -f %{_sysconfdir}/watchquagga.*
%endif

if [ ! -e %{_sysconfdir}/vtysh.conf ]; then
	touch %{_sysconfdir}/vtysh.conf
	chmod 640 %{_sysconfdir}/vtysh.conf
%if 0%{?vty_group:1}
    chown quagga:%{vty_group} %{_sysconfdir}/vtysh.conf*
%endif
fi

%postun
if [ "$1" -ge 1 ]; then
	# Find out which daemons need to be restarted.
	for daemon in %all_daemons ; do
		if [ -f /var/lock/subsys/${daemon} ]; then
			eval restart_${daemon}=yes
		else
			eval restart_${daemon}=no
		fi
	done
	# Rename restart flags for daemons handled specially.
	running_zebra="$restart_zebra"
	restart_zebra=no
	%if %{with_watchquagga}
		running_watchquagga="$restart_watchquagga"
		restart_watchquagga=no
	%endif
	
	%if "%{initsystem}" == "systemd"
		##
		## Systemd Version
		##
		# No watchquagga for systemd version
		#
		# Stop all daemons other than zebra.
		for daemon in %all_daemons ; do
			eval restart=\$restart_${daemon}
			[ "$restart" = yes ] && \
				%systemd_postun_with_restart ${daemon}.service
		done
		# Restart zebra.
		[ "$running_zebra" = yes ] && \
			%systemd_postun_with_restart $daemon.service
		# Start all daemons other than zebra.
		for daemon in %all_daemons ; do
			eval restart=\$restart_${daemon}
			[ "$restart" = yes ] && \
				%systemd_post ${daemon}.service
		done
	%else
		##
		## init.d Version
		##
		%if %{with_watchquagga}
			# Stop watchquagga first.
			[ "$running_watchquagga" = yes ] && \
				/etc/rc.d/init.d/watchquagga stop >/dev/null 2>&1
		%endif
		# Stop all daemons other than zebra and watchquagga.
		for daemon in %all_daemons ; do
			eval restart=\$restart_${daemon}
			[ "$restart" = yes ] && \
				/etc/rc.d/init.d/${daemon} stop >/dev/null 2>&1
		done
		# Restart zebra.
		[ "$running_zebra" = yes ] && \
			/etc/rc.d/init.d/zebra restart >/dev/null 2>&1
		# Start all daemons other than zebra and watchquagga.
		for daemon in %all_daemons ; do
			eval restart=\$restart_${daemon}
			[ "$restart" = yes ] && \
				/etc/rc.d/init.d/${daemon} start >/dev/null 2>&1
		done
		%if %{with_watchquagga}
			# Start watchquagga last.
			# Avoid postun scriptlet error if watchquagga is not running. 
			[ "$running_watchquagga" = yes ] && \
				/etc/rc.d/init.d/watchquagga start >/dev/null 2>&1 || :
		%endif	
	%endif
fi

if [ -f %{_infodir}/%{name}.inf* ]; then
	/sbin/install-info --delete %{_infodir}/quagga.info %{_infodir}/dir
fi

%preun
%if "%{initsystem}" == "systemd"
	##
	## Systemd Version
	##
	if [ "$1" = "0" ]; then
		for daemon in %all_daemons ; do
			%systemd_preun ${daemon}.service
		done
	fi
%else
	##
	## init.d Version
	##
	if [ "$1" = "0" ]; then
		for daemon in %all_daemons ; do
			/etc/rc.d/init.d/${daemon} stop >/dev/null 2>&1
			/sbin/chkconfig --del ${daemon}
		done
	fi
%endif

%clean
%if !0%{?keep_build:1}
rm -rf %{buildroot}
%endif

%files
%defattr(-,root,root)
%doc */*.sample* AUTHORS COPYING
%if %{with_texi2html}
	%doc doc/quagga.html
%endif
%doc doc/mpls
%doc ChangeLog INSTALL NEWS README REPORTING-BUGS SERVICES TODO
%if 0%{?quagga_user:1}
%dir %attr(751,%quagga_user,%quagga_user) %{_sysconfdir}
%dir %attr(750,%quagga_user,%quagga_user) /var/log/quagga 
%dir %attr(751,%quagga_user,%quagga_user) /var/run/quagga
%else
%dir %attr(750,root,root) %{_sysconfdir}
%dir %attr(750,root,root) /var/log/quagga
%dir %attr(750,root,root) /var/run/quagga
%endif
%if 0%{?vty_group:1}
%attr(750,%quagga_user,%vty_group) %{_sysconfdir}/vtysh.conf.sample
%endif
%{_infodir}/quagga.info*.gz
%{_mandir}/man*/*
%if %{with_watchquagga}
	%{_mandir}/man*/watchquagga.*
%endif
%{_sbindir}/zebra
%{_sbindir}/ospfd
%{_sbindir}/ripd
%{_sbindir}/bgpd
%if %{with_watchquagga}
	%{_sbindir}/watchquagga
%endif
%{_sbindir}/ripngd
%{_sbindir}/ospf6d
%if %{with_pimd}
%{_sbindir}/pimd
%endif
%if %{with_isisd}
%{_sbindir}/isisd
%endif
%if %{with_nhrpd}
%{_sbindir}/nhrpd
%endif
%if %{with_shared}
%{_libdir}/quagga/lib*.so
%{_libdir}/quagga/lib*.so.?
%attr(755,root,root) %{_libdir}/quagga/lib*.so.?.?.?
%endif
%if %{with_vtysh}
%{_bindir}/*
%endif
%config /etc/quagga/[!v]*
%if "%{initsystem}" == "systemd"
	%{_unitdir}/*.service
%else
	%config /etc/rc.d/init.d/zebra
	%if %{with_watchquagga}
		%config /etc/rc.d/init.d/watchquagga
	%endif
	%config /etc/rc.d/init.d/ripd
	%config /etc/rc.d/init.d/ospfd
	%config /etc/rc.d/init.d/bgpd
	%config /etc/rc.d/init.d/ripngd
	%config /etc/rc.d/init.d/ospf6d
	%if %{with_isisd}
		%config /etc/rc.d/init.d/isisd
	%endif
	%if %{with_pimd}
		%config /etc/rc.d/init.d/pimd
	%endif
	%if %{with_nhrpd}
		%config /etc/rc.d/init.d/nhrpd
	%endif
%endif
%config(noreplace) /etc/sysconfig/quagga
%config(noreplace) /etc/pam.d/quagga
%config(noreplace) %attr(640,root,root) /etc/logrotate.d/*
%{_tmpfilesdir}/quagga.conf

%files contrib
%defattr(-,root,root)
%doc AUTHORS COPYING %attr(0644,root,root) tools

%files devel
%defattr(-,root,root)
%doc AUTHORS COPYING
%if %{with_ospfclient}
%{_sbindir}/ospfclient
%endif
%dir %{_libdir}/quagga/
%{_libdir}/quagga/*.a
%{_libdir}/quagga/*.la
%dir %attr(755,root,root) %{_includedir}/%{name}
%{_includedir}/%name/*.h
%dir %attr(755,root,root) %{_includedir}/%{name}/ospfd
%{_includedir}/%name/ospfd/*.h
%if %{with_ospfapi}
%dir %attr(755,root,root) %{_includedir}/%{name}/ospfapi
%{_includedir}/%name/ospfapi/*.h
%endif

%changelog
* Sun Mar 5 2017 Paul Jakma <paul@jakma.org>
- Fix lint errors
- Make texi2html conditional, disable by default to avoid needing TeX
  by default

* Mon Feb 27 2017 Paul Jakma <paul@jakma.org>
- Apply 0001-systemd-various-service-file-improvements.patch from Fedora
- Review Fedora spec file and sync up with any useful differences, inc:
- Add tmpfiles.d config for Quagga from Fedora
- Add quagga-filter-perl-requires.sh from Fedora.
- Move libs to %%{_libdir}/quagga as per Fedora
- use systemd_postun_with_restart for postun

* Tue Feb 14 2017 Timo Teräs <timo.teras@iki.fi>
- add nhrpd

* Thu Feb 11 2016 Paul Jakma <paul@jakma.org>
- remove with_ipv6 conditionals, always build v6
- Fix UTF-8 char in spec changelog
- remove quagga.pam.stack, long deprecated.

* Thu Oct 22 2015 Martin Winter <mwinter@opensourcerouting.org>
- Cleanup configure: remove --enable-ipv6 (default now), --enable-nssa,
    --enable-netlink
- Remove support for old fedora 4/5
- Fix for package nameing
- Fix Weekdays of previous changelogs (bogus dates)
- Add conditional logic to only build tex footnotes with supported texi2html 
- Added pimd to files section and fix double listing of /var/lib*/quagga
- Numerous fixes to unify upstart/systemd startup into same spec file
- Only allow use of watchquagga for non-systemd systems. no need with systemd

* Fri Sep  4 2015 Paul Jakma <paul@jakma.org>
- buildreq updates
- add a default define for with_pimd

* Mon Sep 12 2005 Paul Jakma <paul@dishone.st>
- Steal some changes from Fedora spec file:
- Add with_rtadv variable
- Test for groups/users with getent before group/user adding
- Readline need not be an explicit prerequisite
- install-info delete should be postun, not preun

* Wed Jan 12 2005 Andrew J. Schorr <ajschorr@alumni.princeton.edu>
- on package upgrade, implement careful, phased restart logic
- use gcc -rdynamic flag when linking for better backtraces

* Wed Dec 22 2004 Andrew J. Schorr <ajschorr@alumni.princeton.edu>
- daemonv6_list should contain only IPv6 daemons

* Wed Dec 22 2004 Andrew J. Schorr <ajschorr@alumni.princeton.edu>
- watchquagga added
- on upgrade, all daemons should be condrestart'ed
- on removal, all daemons should be stopped

* Mon Nov 08 2004 Paul Jakma <paul@dishone.st>
- Use makeinfo --html to generate quagga.html

* Sun Nov 07 2004 Paul Jakma <paul@dishone.st>
- Fix with_ipv6 set to 0 build

* Sat Oct 23 2004 Paul Jakma <paul@dishone.st>
- Update to 0.97.2

* Sat Oct 23 2004 Andrew J. Schorr <aschorr@telemetry-investments.com>
- Make directories be owned by the packages concerned
- Update logrotate scripts to use correct path to killall and use pid files

* Fri Oct 08 2004 Paul Jakma <paul@dishone.st>
- Update to 0.97.0

* Wed Sep 15 2004 Paul Jakma <paul@dishone.st>
- build snmp support by default
- build irdp support
- build with shared libs
- devel subpackage for archives and headers

* Thu Jan 08 2004 Paul Jakma <paul@dishone.st>
- updated sysconfig files to specify local dir
- added ospf_dump.c crash quick fix patch
- added ospfd persistent interface configuration patch

* Tue Dec 30 2003 Paul Jakma <paul@dishone.st>
- sync to CVS
- integrate RH sysconfig patch to specify daemon options (RH)
- default to have vty listen only to 127.1 (RH)
- add user with fixed UID/GID (RH)
- create user with shell /sbin/nologin rather than /bin/false (RH)
- stop daemons on uninstall (RH)
- delete info file on preun, not postun to avoid deletion on upgrade. (RH)
- isisd added
- cleanup tasks carried out for every daemon

* Sun Nov 2 2003 Paul Jakma <paul@dishone.st>
- Fix -devel package to include all files
- Sync to 0.96.4

* Tue Aug 12 2003 Paul Jakma <paul@dishone.st>
- Renamed to Quagga
- Sync to Quagga release 0.96

* Thu Mar 20 2003 Paul Jakma <paul@dishone.st>
- zebra privileges support

* Tue Mar 18 2003 Paul Jakma <paul@dishone.st>
- Fix mem leak in 'show thread cpu'
- Ralph Keller's OSPF-API
- Amir: Fix configure.ac for net-snmp

* Sat Mar 1 2003 Paul Jakma <paul@dishone.st>
- ospfd IOS prefix to interface matching for 'network' statement
- temporary fix for PtP and IPv6
- sync to zebra.org CVS

* Mon Jan 20 2003 Paul Jakma <paul@dishone.st>
- update to latest cvs
- Yon's "show thread cpu" patch - 17217
- walk up tree - 17218
- ospfd NSSA fixes - 16681
- ospfd nsm fixes - 16824
- ospfd OLSA fixes and new feature - 16823 
- KAME and ifindex fixes - 16525
- spec file changes to allow redhat files to be in tree

* Sat Dec 28 2002 Alexander Hoogerhuis <alexh@ihatent.com>
- Added conditionals for building with(out) IPv6, vtysh, RIP, BGP
- Fixed up some build requirements (patch)
- Added conditional build requirements for vtysh / snmp
- Added conditional to files for _bindir depending on vtysh

* Mon Nov 11 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- add Greg Troxel's md5 buffer copy/dup fix
- add RIPv1 fix
- add Frank's multicast flag fix

* Wed Oct 09 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- timestamped crypt_seqnum patch
- oi->on_write_q fix

* Mon Sep 30 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- add vtysh 'write-config (integrated|daemon)' patch
- always 'make rebuild' in vtysh/ to catch new commands

* Fri Sep 13 2002 Paul Jakma <paulj@alphyra.ie>
- update to 0.93b

* Wed Sep 11 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- add "/sbin/ip route flush proto zebra" to zebra RH init on startup

* Sat Aug 24 2002 Paul Jakma <paulj@alphyra.ie>
- update to current CVS
- add OSPF point to multipoint patch
- add OSPF bugfixes
- add BGP hash optimisation patch

* Fri Jun 14 2002 Paul Jakma <paulj@alphyra.ie>
- update to 0.93-pre1 / CVS
- add link state detection support
- add generic PtP and RFC3021 support
- various bug fixes

* Thu Aug 09 2001 Elliot Lee <sopwith@redhat.com> 0.91a-6
- Fix bug #51336

* Wed Aug  1 2001 Trond Eivind Glomsrød <teg@redhat.com> 0.91a-5
- Use generic initscript strings instead of initscript specific
  ( "Starting foo: " -> "Starting $prog:" )

* Fri Jul 27 2001 Elliot Lee <sopwith@redhat.com> 0.91a-4
- Bump the release when rebuilding into the dist.

* Tue Feb  6 2001 Tim Powers <timp@redhat.com>
- built for Powertools

* Sun Feb  4 2001 Pekka Savola <pekkas@netcore.fi> 
- Hacked up from PLD Linux 0.90-1, Mandrake 0.90-1mdk and one from zebra.org.
- Update to 0.91a
- Very heavy modifications to init.d/*, .spec, pam, i18n, logrotate, etc.
- Should be quite Red Hat'isque now.
