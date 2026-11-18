module doxygen_brief
  !> @brief Module with Doxygen brief documentation.
  implicit none
contains
  !> @brief Does the thing.
  !!
  !! @param x Input value.
  subroutine documented(x)
    integer, intent(in) :: x
  end subroutine
end module
