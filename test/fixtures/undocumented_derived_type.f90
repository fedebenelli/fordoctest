module m
  !! Module documentation.
  type :: t
    integer :: c
  contains
    procedure :: p
  end type
contains
  subroutine p(self)
    !! Procedure documentation.
    class(t) :: self !! Self documentation.
  end subroutine
end module
