module m
  !! Module documentation.
  type :: t
    !! Type documentation.
    integer :: c !! Component documentation.
  contains
    procedure :: p !! Bound procedure documentation.
  end type

  interface gen
    !! Generic interface documentation.
    module procedure p
  end interface

  interface
    !! Explicit interface documentation.
    module subroutine ext(x)
      integer :: x !! Argument documentation.
    end subroutine
  end interface
contains
  subroutine p(self, x)
    !! Do the thing.
    class(t) :: self !! Self documentation.
    integer :: x !! X documentation.
  end subroutine
end module

submodule (m) sm
  !! Submodule documentation.
contains
  module procedure p
    !! Implementation documentation.
  end procedure

  module procedure ext
    !! External implementation documentation.
  end procedure
end submodule

program main
  !! Program documentation.
  use m
contains
  subroutine helper(y)
    !! Help with the thing.
    integer :: y !! Y documentation.
  end subroutine
end program
