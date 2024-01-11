%global intel_mpi_bench_vers IMB-v2021.3
%global osu_micro_bench_vers 5.8
Summary: MPI Benchmarks and tests
Name: mpitests
Version: 5.8
Release: 1%{?dist}
License: CPL and BSD
Group: Applications/Engineering
# These days we get the benchmark soucres from Intel and OSU directly
# rather than from openfabrics.
URL: http://www.openfabrics.org
# https://software.intel.com/en-us/articles/intel-mpi-benchmarks
Source0: https://github.com/intel/mpi-benchmarks/archive/%{intel_mpi_bench_vers}.tar.gz
Source1: http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-%{osu_micro_bench_vers}.tgz
# Only for old openmpi
#Patch101: OMB-disable-collective-async.patch
BuildRequires: hwloc-devel, libibmad-devel, rdma-core-devel
BuildRequires: automake, autoconf, libtool
BuildRequires: gcc, gcc-c++

%description
A set of popular MPI benchmarks:
Intel MPI benchmarks %{intel_mpi_bench_vers}.
OSU micro-benchmarks %{osu_micro_bench_vers}.

# openmpi 3.0.0 dropped support for big endian ppc
%ifnarch ppc ppc64
%package openmpi
Summary: MPI tests package compiled against openmpi
Group: Applications
BuildRequires: openmpi-devel >= 3.1.2-2
Requires: openmpi%{?_isa}
%description openmpi
MPI test suite compiled against the openmpi package
%endif

%package mpich
Summary: MPI tests package compiled against mpich
Group: Applications
BuildRequires: mpich-devel >= 3.2.1-8
Requires: mpich%{?_isa}
%description mpich
MPI test suite compiled against the mpich package

# mvapich2 is not yet built on s390(x)
%ifnarch s390 s390x
%package mvapich2
Summary: MPI tests package compiled against mvapich2
Group: Applications
BuildRequires: mvapich2-devel >= 2.3-2
Requires: mvapich2%{?_isa}
%description mvapich2
MPI test suite compiled against the mvapich2 package
%endif

# PSM is x86_64-only
%ifarch x86_64
%package mvapich2-psm2
Summary: MPI tests package compiled against mvapich2 using OmniPath
Group: Applications
BuildRequires: mvapich2-psm2-devel >= 2.3-2
BuildRequires: libpsm2-devel
Requires: mvapich2-psm2%{?_isa}
%description mvapich2-psm2
MPI test suite compiled against the mvapich2 package using OmniPath
%endif

%prep
%setup -c 
%setup -T -D -a 1
cd osu-micro-benchmarks-5.8
cd ..

%build
# We don't do a non-mpi version of this package, just straight to the mpi builds
export CC=mpicc
export CXX=mpicxx
export FC=mpif90
export F77=mpif77
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -fPIC"
export CXXFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -fPIC"
do_build() {
  mkdir build-$MPI_COMPILER
  cp -al mpi-benchmarks-%{intel_mpi_bench_vers} osu-micro-benchmarks-%{osu_micro_bench_vers} build-$MPI_COMPILER
  cd build-$MPI_COMPILER/mpi-benchmarks-%{intel_mpi_bench_vers}
  make OPTFLAGS="%{build_cflags}" LDFLAGS="%{build_ldflags}" MPI_HOME="$MPI_HOME" all
  cd ../osu-micro-benchmarks-%{osu_micro_bench_vers}
  autoreconf -vif
  %configure
  make %{?_smp_mflags}
  cd ../..
}

# do N builds, one for each mpi stack
%ifnarch ppc ppc64
%{_openmpi_load}
do_build
%{_openmpi_unload}
%endif

%{_mpich_load}
do_build
%{_mpich_unload}

%ifnarch s390 s390x
%{_mvapich2_load}
do_build
%{_mvapich2_unload}

%endif

%ifarch x86_64
%{_mvapich2_psm2_load}
do_build
%{_mvapich2_psm2_unload}
%endif

%install
do_install() {
  mkdir -p %{buildroot}$MPI_BIN
  cd build-$MPI_COMPILER/osu-micro-benchmarks-%{osu_micro_bench_vers}
  make install DESTDIR=%{buildroot}/staging
  find %{buildroot}/staging -name 'osu_*' -type f -perm -111 | while read X; do
    mv $X %{buildroot}$MPI_BIN/mpitests-$(basename $X)
  done
  cd ../mpi-benchmarks-%{intel_mpi_bench_vers}/
  for X in IMB-*; do
    cp $X %{buildroot}$MPI_BIN/mpitests-$X
  done
  cd ../..
}

# do N installs, one for each mpi stack
%ifnarch ppc ppc64
%{_openmpi_load}
do_install
%{_openmpi_unload}
%endif

%{_mpich_load}
do_install
%{_mpich_unload}

%ifnarch s390 s390x
%{_mvapich2_load}
do_install
%{_mvapich2_unload}
%endif

%ifarch x86_64
%{_mvapich2_psm2_load}
do_install
%{_mvapich2_psm2_unload}
%endif

%ifnarch ppc ppc64
%files openmpi
%{_libdir}/openmpi/bin/mpitests-*
%endif

%files mpich
%{_libdir}/mpich/bin/mpitests-*

%ifnarch s390 s390x
%files mvapich2
%{_libdir}/mvapich2/bin/mpitests-*
%endif

%ifarch x86_64
%files mvapich2-psm2
%{_libdir}/mvapich2-psm2/bin/mpitests-*
%endif

%changelog
* Fri Dec 10 2021 Honggang Li <honli@redhat.com> - 5.8-1
- Update OSU benchmarks to upstream release 5.8
- Update Intel MPI Benchmarks 2021.3
- Resolves: rhbz#2008517

* Thu May 13 2021 Honggang Li <honli@redhat.com> - 5.7-2
- Update OSU benchmarks to upstream release 5.7.1
- Update Intel MPI Benchmarks 2021.2
- Resolves: rhbz#1960078

* Tue Dec 22 2020 Honggang Li <honli@redhat.com> - 5.7-1
- Update OSU benchmarks to upstream release 5.7
- Resolves: rhbz#1909632

* Thu Oct 15 2020 Honggang Li <honli@redhat.com> - 5.6.3-1
- Update OSU benchmarks to upstream release 5.6.3
- Resolves: rhbz#1888568

* Tue May 12 2020 Honggang Li <honli@redhat.com> - 5.6.2-1
- Update OSU benchmarks to upstream release 5.6.2
- Update IMB benchmarks to upstream release v2019.6
- Resolves: rhbz#1817837

* Sat Sep 22 2018 Jarod Wilson <jarod@redhat.com> - 5.4.2-4
- Properly fix build and linker flags, annocheck now silent
- Resolves: rhbz#1624145

* Tue Sep 18 2018 Jarod Wilson <jarod@redhat.com> - 5.4.2-3
- First wave of compiler flag usage fixups from annobin scans
- Related: rhbz#1624145

* Thu Sep 13 2018 Jarod Wilson <jarod@redhat.com> - 5.4.2-2
- Rebuild with updated openmpi, mvapich and mpich for proper deps
- Resolves: rhbz#1628627

* Thu Aug 16 2018 Jarod Wilson <jarod@redhat.com> - 5.4.2-1
- Initial build for RHEL8, based on latest RHEL7 package
- Resolves: rhbz#1556959
