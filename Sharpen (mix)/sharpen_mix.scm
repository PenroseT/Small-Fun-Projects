; The GIMP -- an image manipulation program
; Copyright (C) 1995 Spencer Kimball and Peter Mattis
;
; Image sharpening tool which uses the combination
; of the gradient and Laplacian filters (the first
; and the second derivative)
; Copyright (C) 2025 Luka Antonic <lukaantonicx@gmail.com>
;
;-----------------------------------------------------------------------
; This program is free software; you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation; either version 2 of the License, or
; (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with this program; if not, write to the Free Software
; Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
;-----------------------------------------------------------------------



; The GEGL plugin plug-in-convmatrix which is used in the script calculates
; the convolution filter by applying an appropriate 5x5 convolution matrix.
; The matrix is not a built-in Scheme type; the nxm matrix is defined as
; an n-length vector (number of rows) whose entries are m-length vectors (columns).
; One could define the matrix type and methods for setting and getting 
; elements of the matrix. However, since I'm using only one of the two 
; variations of the Laplace matrix for the filter, I will define these matrices
; directly.

(define (matrix_laplace diagonal?)
	(let* ((matl
			 (if (eqv? diagonal? TRUE)
				 (vector 
						0.0 0.0 0.0 0.0 0.0 
                        0.0 1.0 1.0 1.0 0.0
                        0.0 1.0 -8.0 1.0 0.0 
                        0.0 1.0 1.0 1.0 0.0 
                        0.0 0.0 0.0 0.0 0.0)
				(vector
					    0 0 0 0 0
					    0 0 1 0 0
					    0 1 -4 1 0
					    0 0 1 0 0
					    0 0 0 0 0
				)
			 )
		  ))
		matl
	)
)


; The channels vector, which is one of the inputs for the plug-in-convmatrix,
; is a 5-element vector whose entries specify channels for which the filter
; is applied. The five entries in order are GRAY, RED, GREEN, BLUE, AND ALPHA.
; This filter is built so that the user can specify if they want to apply
; the filter only to the GRAY channel or for the three color channels (RGB).
 

(define (channels_set rgb?)
	(let* ((channels
		  	(if (eqv? rgb? TRUE) 
				(vector TRUE TRUE TRUE TRUE FALSE)
				(vector TRUE FALSE FALSE FALSE FALSE)	
			)	
		  ))
		channels
	)		
)



(define (script-fu-sharpen-mix in_img in_lyr diagonal? blur_radius)
	(let*(
		 (img in_img)
		 (lyr in_lyr)
		 (lyr_width (car (gimp-drawable-width lyr)))
		 (lyr_height (car (gimp-drawable-height lyr)))
		 (lyr_group (car (gimp-layer-group-new img)))
		 (lyr_mask_laplace (car (gimp-layer-copy lyr FALSE)))
		 (lyr_mask_gradient (car (gimp-layer-copy lyr FALSE)))		 

		 (matrix_argc 25)     ; The number of elements of the matrix
							  ; It has to be defined for plug-in-convmatrix
							  ; to work
		 (channels_argc 5)
		 (bmode 0)            ; Border mode, 0 is EXTEND (I suppose this means
							  ; padding with zeros), add the possibility for user to choose this
		 
		 (laplace (matrix_laplace diagonal?))
		 (channels (vector TRUE TRUE TRUE TRUE FALSE))	 	
		 )
	
	   
	(gimp-image-undo-group-start img)
    (gimp-image-insert-layer img lyr_group 0 0)

	(gimp-image-insert-layer img lyr_mask_laplace lyr_group 0)	
	(gimp-image-insert-layer img lyr_mask_gradient lyr_group 0)	
    
	(plug-in-convmatrix RUN-NONINTERACTIVE img lyr_mask_laplace matrix_argc laplace
					    FALSE 1 0 channels_argc channels bmode)	


	; TRUE is chosen both for the vertical and the horizontal direction of the 
	; gradient. In this case the filter is calculated as a root mean square (RMS)
    ; of the horizontal gradient (gx) and the vertical gradient (gy), i.e. as
	; sqrt((gx^2+gy^2)/2).

    (plug-in-sobel RUN-NONINTERACTIVE img lyr_mask_gradient TRUE TRUE FALSE) 
	
	; I should add an option to choose between few different smoothing filters,
	; for instance, box and Gaussian spatial filter and low-pass frequency
	; filter.
	(plug-in-gauss RUN-NONINTERACTIVE img lyr_mask_gradient blur_radius blur_radius 0)

	(gimp-image-undo-group-end img)
	(gimp-displays-flush)

	)	
)


(script-fu-register
		"script-fu-sharpen-mix"
		"Sharpen (mix)"
		"The filter applies a mask that is added
		to the original image. The mask is formed by
		multiplying the Laplacian fiter with the smoothed
		Sobel gradient of the image. The dynamic range of
		the image is increased to a power-law gamma transform"
		"Luka Antonic"
		"Copyright 2025, Luka Antonic"
		"Mar 11, 2025"
		"RGB* GRAY*"

		SF-IMAGE			"Image"            							       0	
		SF-DRAWABLE			"Layer"            						           0
		SF-TOGGLE           "Include diagonals for the Laplace operator?"      TRUE
		SF-ADJUSTMENT       "Smooth radius"                                    '(5 1 50 1 10 0 0)
)

(script-fu-menu-register "script-fu-sharpen-mix" "<Image>/Filters/Enhance")
