%define debug_package %{nil}
%define _enable_debug_packages %{nil}

# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel
%global pkg ruby27

# Force Software Collections on
%global _scl_prefix %{ns_dir}
%global scl %{ns_name}-%{pkg}
# HACK: OBS Doesn't support macros in BuildRequires statements, so we have
#       to hard-code it here.
# https://en.opensuse.org/openSUSE:Specfile_guidelines#BuildRequires
%global scl_prefix %{scl}-
%{?scl:%scl_package libuv}
%{!?scl:%global pkg_name %{name}}
%global somajor 1
%global sominor 0
%global sonano 0
%global sofull %{somajor}.%{sominor}.%{sonano}

# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define release_prefix 1

Name: %{?scl_prefix}libuv
Epoch:   1
Version: 1.51.0
Release: %{release_prefix}%{?dist}.cpanel
Summary: libuv is a multi-platform support library with a focus on asynchronous I/O.

# the licensing breakdown is described in detail in the LICENSE file
License: https://github.com/libuv/libuv/blob/v1.x/LICENSE

BuildRequires: cmake3
BuildRequires: libuv

%if 0%{?rhel} < 8
BuildRequires: python
BuildRequires: devtoolset-8-toolchain
BuildRequires: devtoolset-8-libatomic-devel
BuildRequires: devtoolset-8-gcc
BuildRequires: devtoolset-8-gcc-c++
%else
BuildRequires: python36
BuildRequires: platform-python
BuildRequires: brotli
BuildRequires: libnghttp2
%endif

BuildRequires: scl-utils
BuildRequires: scl-utils-build
%{?scl:Requires:%scl_runtime}
%{?scl:BuildRequires: %{scl}-runtime}

URL: http://libuv.org/
Source0: http://dist.libuv.org/dist/v%{version}/libuv-v%{version}.tar.gz
Source2: libuv.pc.in

%{?scl:BuildRequires: %{?scl}-runtime}

Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
libuv is a multi-platform support library with a focus on asynchronous I/O. It
was primarily developed for use by Node.js, but it's also used by Luvit,
Julia, pyuv, and others.

%package devel
Summary: Development libraries for libuv
Group: Development/Libraries
Requires: %{?scl_prefix}%{pkg_name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: pkgconfig
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description devel
Development libraries for libuv

%prep
%setup -q -n %{pkg_name}-v%{version}

%build
%if 0%{?rhel} < 8
. /opt/rh/devtoolset-8/enable
%endif

export CFLAGS='%{optflags}'
export CXXFLAGS='%{optflags}'

mkdir -p build
(cd build && cmake3 .. -DBUILD_TESTING=ON)
cmake3 --build build

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_includedir}
install -d %{buildroot}%{_libdir}

install -pm644 include/uv.h %{buildroot}%{_includedir}

mkdir -p -m 0777 %{buildroot}%{_includedir}/uv/
cp include/uv/* %{buildroot}%{_includedir}/uv/
chmod 0644 %{buildroot}%{_includedir}/uv/*
chmod 0755 %{buildroot}%{_includedir}/uv

install build/libuv.so.%{sofull}  %{buildroot}%{_libdir}/libuv.so.%{?scl:%{scl_name}-}%{version}
ln -sf %{_libdir}/libuv.so.%{?scl:%{scl_name}-}%{version} %{buildroot}%{_libdir}/libuv.so.%{sofull}
ln -sf %{_libdir}/libuv.so.%{?scl:%{scl_name}-}%{version} %{buildroot}%{_libdir}/libuv.so.%{somajor}
ln -sf %{_libdir}/libuv.so.%{?scl:%{scl_name}-}%{version} %{buildroot}%{_libdir}/libuv.so

cp include/uv.h \
   %{buildroot}/%{_includedir}

# Create the pkgconfig file
mkdir -p %{buildroot}/%{_libdir}/pkgconfig

sed -e "s#@prefix@#%{_prefix}#g" \
    -e "s#@exec_prefix@#%{_exec_prefix}#g" \
    -e "s#@libdir@#%{_libdir}#g" \
    -e "s#@includedir@#%{_includedir}#g" \
    -e "s#@version@#%{version}#g" \
    %SOURCE2 > %{buildroot}/%{_libdir}/pkgconfig/libuv.pc

%check
# Tests are currently disabled because some require network access
# Working with upstream to split these out
#./out/Release/run-tests
#./out/Release/run-benchmarks

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc README.md AUTHORS LICENSE
%{_libdir}/libuv.so.*

%files devel
%doc README.md AUTHORS LICENSE
%{_libdir}/libuv.so
%{_libdir}/pkgconfig/libuv.pc
%{_includedir}/uv.h
%{_includedir}/uv/*

%changelog
* Fri Apr 25 2025 Cory McIntire <cory.mcintire@webpros.com> - 1.51.0-1
- EA-12835: Update ea-ruby27-libuv from v1.50.0 to v1.51.0

* Wed Feb 05 2025 Cory McIntire <cory.mcintire@webpros.com> - 1.50.0-1
- EA-12684: Update ea-ruby27-libuv from v1.48.0 to v1.50.0

* Tue Oct 08 2024 Cory McIntire <cory@cpanel.net> - 1.49.0-2
- EA-12450: Rolling “ea-ruby27-libuv” back to “757c822adb9bc99291dfd5219b5afa32e63e1fd4”: upstream issue causing upload limit problems
- Actual version is 1.48.0-3

* Fri Sep 27 2024 Cory McIntire <cory@cpanel.net> - 1.49.0-1
- EA-12429: Update ea-ruby27-libuv from v1.48.0 to v1.49.0

* Wed Feb 07 2024 Cory McIntire <cory@cpanel.net> - 1.48.0-1
- EA-11958: Update ea-ruby27-libuv from v1.47.0 to v1.48.0
- CVE-2024-24806: Improper Domain Lookup that potentially leads to SSRF attacks

* Tue Nov 07 2023 Cory McIntire <cory@cpanel.net> - 1.47.0-1
- EA-11789: Update ea-ruby27-libuv from v1.46.0 to v1.47.0

* Wed Jul 05 2023 Cory McIntire <cory@cpanel.net> - 1.46.0-1
- EA-11533: Update ea-ruby27-libuv from v1.45.0 to v1.46.0

* Mon May 22 2023 Cory McIntire <cory@cpanel.net> - 1.45.0-1
- EA-11427: Update ea-ruby27-libuv from v1.44.2 to v1.45.0

* Wed May 17 2023 Julian Brown <julian.brown@cpanel.net> - 1.44.2-3
- ZC-10950: Fix build problems

* Mon May 08 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 1.44.2-2
- ZC-10936: Clean up Makefile and remove debug-package-nil

* Tue Jul 12 2022 Cory McIntire <cory@cpanel.net> - 1.44.2-1
- EA-10826: Update ea-ruby27-libuv from v1.44.1 to v1.44.2

* Thu Mar 10 2022 Cory McIntire <cory@cpanel.net> - 1.44.1-1
- EA-10547: Update ea-ruby27-libuv from v1.44.0 to v1.44.1

* Mon Mar 07 2022 Cory McIntire <cory@cpanel.net> - 1.44.0-1
- EA-10536: Update ea-ruby27-libuv from v1.43.0 to v1.44.0

* Wed Jan 05 2022 Cory McIntire <cory@cpanel.net> - 1.43.0-1
- EA-10407: Update ea-ruby27-libuv from v1.42.0 to v1.43.0

* Tue Dec 28 2021 Dan Muey <dan@cpanel.net> - 1.42.0-2
- ZC-9589: Update DISABLE_BUILD to match OBS

* Thu Jul 22 2021 Cory McIntire <cory@cpanel.net> - 1.42.0-1
- EA-9983: Update ea-ruby27-libuv from v1.41.0 to v1.42.0

* Thu Feb 25 2021 Cory McIntire <cory@cpanel.net> - 1.41.0-1
- EA-9603: Update ea-ruby27-libuv from v1.39.0 to v1.41.0

* Tue Sep 08 2020 Julian Brown <julian.brown@cpanel.net> - 1.39.0-1
ZC-7502 - Initial package of libuv for the ea-ruby27 SCL

